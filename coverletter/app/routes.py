
from app.utils import extract_text_from_file, generate_cover_letter
import openai
import os
from flask import render_template, request, jsonify, send_from_directory
from app.utils import create_docx
from app.utils import create_pdf

def create_routes(app):
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/upload", methods=["POST"])
    def upload_files():
        try:
            # Get form data and files
            job_description = request.form.get("job_description")
            cv_file = request.files.get("cv")

            if not job_description or not cv_file:
                return jsonify({"error": "Both job description and CV are required."}), 400

            # Save uploaded CV file
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            cv_path = os.path.join(app.config["UPLOAD_FOLDER"], cv_file.filename)
            cv_file.save(cv_path)

            # Extract text from the CV
            cv_text = extract_text_from_file(cv_path)

            # Generate cover letter
            cover_letter = generate_cover_letter(job_description, cv_text)

            # Paths for the generated files
            pdf_filename = "cover_letter.pdf"
            docx_filename = "cover_letter.docx"
            pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_filename)
            docx_path = os.path.join(app.config["UPLOAD_FOLDER"], docx_filename)

            # Save files
            create_pdf(cover_letter, pdf_path)
            create_docx(cover_letter, docx_path)

            # Log file locations for debugging
            print(f"PDF saved at: {pdf_path}")
            print(f"DOCX saved at: {docx_path}")

            return jsonify({
                "message": "Cover letter generated successfully.",
                "pdf_url": f"/download/{pdf_filename}",
                "docx_url": f"/download/{docx_filename}",
            })

        except ValueError as e:
            return jsonify({"error": f"Value Error: {str(e)}"}), 400
        except openai.OpenAIError as e:
            return jsonify({"error": f"OpenAI API error: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    @app.route("/download/<filename>")
    def download_file(filename):
        """Serve the requested file for download."""
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(file_path):
            print(f"File found: {file_path}")  # Debugging log
            return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
        else:
            print(f"File not found: {file_path}")  # Debugging log
            return jsonify({"error": "File not found."}), 404
