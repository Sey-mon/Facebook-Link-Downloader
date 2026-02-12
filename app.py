from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
from pathlib import Path
import threading

app = Flask(__name__)

# Create downloads folder
DOWNLOAD_FOLDER = Path("downloads")
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

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
    """Download the video"""
    url = request.json.get('url')
    format_id = request.json.get('format_id', 'best')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # Use format_id if provided, otherwise use best
        format_spec = format_id if format_id != 'best' else 'best[ext=mp4]/best'
        
        ydl_opts = {
            'format': format_spec,
            'outtmpl': str(DOWNLOAD_FOLDER / '%(title)s.%(ext)s'),
            'quiet': False,
            'no-warnings': True,
            'socket_timeout': 30,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            return jsonify({
                'success': True,
                'message': f'Successfully downloaded: {info.get("title")}',
                'filename': os.path.basename(filename)
            })
    
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 400

@app.route('/downloads', methods=['GET'])
def list_downloads():
    """List downloaded files"""
    try:
        files = list(DOWNLOAD_FOLDER.glob('*'))
        downloads = [
            {
                'name': f.name,
                'size': f.stat().st_size / (1024*1024),  # Convert to MB
                'path': f'/download-file/{f.name}'
            }
            for f in files if f.is_file()
        ]
        downloads.sort(key=lambda x: x['name'])
        return jsonify(downloads)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/download-file/<filename>', methods=['GET'])
def download_file(filename):
    """Serve file for download to user's device"""
    try:
        file_path = DOWNLOAD_FOLDER / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='video/mp4'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
