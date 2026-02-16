from flask import Flask, render_template, request, jsonify, send_file, Response
from whitenoise import WhiteNoise
import yt_dlp
import os
from pathlib import Path
import tempfile
import uuid

app = Flask(__name__)

# Configure static files for production with WhiteNoise
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='static/')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Use temporary directory for downloads
TEMP_FOLDER = Path(tempfile.gettempdir()) / 'fb_downloader'
TEMP_FOLDER.mkdir(exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-info', methods=['POST'])
def get_info():
    """Get video info and available formats"""
    url = request.json.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        ydl_opts = {
            'quiet': True,
            'no-warnings': True,
            'socket_timeout': 10
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract format information
            formats = []
            if 'formats' in info:
                for fmt in info.get('formats', []):
                    # Only include video formats
                    if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                        formats.append({
                            'format_id': fmt.get('format_id'),
                            'ext': fmt.get('ext'),
                            'height': fmt.get('height'),
                            'width': fmt.get('width'),
                            'fps': fmt.get('fps'),
                            'filesize_approx': fmt.get('filesize_approx'),
                            'description': f"{fmt.get('height', 'unknown')}p - {fmt.get('ext', 'unknown')}"
                        })
            
            # Sort by height descending
            formats.sort(key=lambda x: x.get('height') or 0, reverse=True)
            
            # Remove duplicates (keep best quality of each resolution)
            seen_heights = set()
            unique_formats = []
            for fmt in formats:
                height = fmt.get('height')
                if height not in seen_heights:
                    unique_formats.append(fmt)
                    seen_heights.add(height)
            
            return jsonify({
                'success': True,
                'title': info.get('title', 'Facebook Video'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'formats': unique_formats[:5]  # Top 5 formats
            })
    
    except Exception as e:
        return jsonify({'error': f'Error fetching video info: {str(e)}'}), 400

@app.route('/download', methods=['POST'])
def download():
    """Download the video directly to user's device"""
    url = request.json.get('url')
    format_id = request.json.get('format_id', 'best')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # Use format_id if provided, otherwise use best
        format_spec = format_id if format_id != 'best' else 'best[ext=mp4]/best'
        
        # Generate unique filename to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        
        ydl_opts = {
            'format': format_spec,
            'outtmpl': str(TEMP_FOLDER / f'{unique_id}_%(title)s.%(ext)s'),
            'quiet': False,
            'no-warnings': True,
            'socket_timeout': 30,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            
            # Return the download URL
            filename = os.path.basename(filepath)
            return jsonify({
                'success': True,
                'download_url': f'/get-file/{filename}',
                'filename': filename.replace(f'{unique_id}_', '')  # Clean filename for user
            })
    
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 400

@app.route('/get-file/<filename>', methods=['GET'])
def get_file(filename):
    """Serve file for download to user's device and delete after sending"""
    try:
        file_path = TEMP_FOLDER / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found or expired'}), 404
        
        # Clean up the unique ID from filename for user
        clean_filename = filename.split('_', 1)[1] if '_' in filename else filename
        
        def generate():
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    yield chunk
            # Delete file after sending
            try:
                os.remove(file_path)
            except:
                pass
        
        return Response(
            generate(),
            mimetype='video/mp4',
            headers={
                'Content-Disposition': f'attachment; filename="{clean_filename}"',
                'Content-Length': str(os.path.getsize(file_path))
            }
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
