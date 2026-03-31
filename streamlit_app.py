import streamlit as st
import requests
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

# 🔗 Backend API
API_URL = "http://127.0.0.1:5000/generate"

st.set_page_config(page_title="DDR Generator", layout="centered")

st.title("🏗️ DDR Report Generator")

# 📂 Upload files
insp = st.file_uploader("Upload Inspection PDF", type=["pdf"])
therm = st.file_uploader("Upload Thermal PDF", type=["pdf"])

# 📝 Context input
context = st.text_area("Additional Context")

# 🔥 PDF generator function
def create_pdf(data):
    styles = getSampleStyleSheet()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(temp_file.name)

    content = []

    for key, value in data.items():
        content.append(Paragraph(f"<b>{key}</b>", styles["Heading3"]))
        content.append(Spacer(1, 8))
        content.append(Paragraph(str(value), styles["Normal"]))
        content.append(Spacer(1, 12))

    doc.build(content)
    return temp_file.name


# 🚀 Button
if st.button("Generate Report"):

    if not insp and not therm:
        st.warning("⚠️ Upload at least one file")
    else:
        files = {}

        # ✅ Convert Streamlit file → proper file stream
        if insp:
            files["inspection"] = (
                insp.name,
                io.BytesIO(insp.getvalue()),
                "application/pdf"
            )

        if therm:
            files["thermal"] = (
                therm.name,
                io.BytesIO(therm.getvalue()),
                "application/pdf"
            )

        try:
            st.info("⏳ Generating report...")

            res = requests.post(
                API_URL,
                files=files,
                data={"context": context},
                timeout=180
            )

            st.write("Status Code:", res.status_code)

            if res.status_code == 200:
                data = res.json()

                # ❗ Handle backend error (Gemini error etc.)
                if "error" in data:
                    st.error(f"❌ {data['error']}")
                else:
                    st.success("✅ Report Generated")
                    st.markdown("## 🏗️ DDR Inspection Report")

                    for key, value in data.items():
                        st.markdown(f"### 🔹 {key.replace('_',' ').title()}")
                        st.write(value)

                    # ✅ Create PDF
                    pdf_path = create_pdf(data)

                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📄 Download PDF",
                            data=f,
                            file_name="DDR_Report.pdf",
                            mime="application/pdf"
                        )

            else:
                st.error(f"❌ Server Error: {res.status_code}")
                st.text(res.text)

        except requests.exceptions.ConnectionError:
            st.error("🚫 Cannot connect to backend. Make sure Flask is running.")

        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Server is slow.")

        except Exception as e:
            st.error(f"⚠️ Unexpected error: {e}")