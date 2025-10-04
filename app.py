import streamlit as st

# =============== Helper Functions ==================
def parse_structure(structure_text):
    """
    Parse the folder/file tree and return batch commands.
    """
    commands = []
    root = None

    for line in structure_text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Root folder
        if line.endswith("/") and root is None:
            root = line.rstrip("/")
            commands.append(f"set ROOT={root}")
            commands.append("mkdir %ROOT%")
            continue

        if root:
            # Clean up tree characters
            path = line.replace("│", "").replace("├──", "").replace("└──", "").strip()
            if not path:
                continue
            if path.endswith("/"):  # folder
                commands.append(f"mkdir %ROOT%\\{path.rstrip('/')}")
            else:  # file
                commands.append(f"type nul > %ROOT%\\{path}")

    return commands, root


def generate_bat(structure_text):
    commands, root = parse_structure(structure_text)
    if not root:
        return None, None

    bat_content = [
        "@echo off",
        *commands,
        'echo ✅ Project structure created successfully!',
        "pause"
    ]
    return "\n".join(bat_content), root


# =============== Streamlit UI ==================
st.set_page_config(page_title="Batch Script Generator", page_icon="⚡", layout="centered")

st.title("⚡ Folder → Batch Script Generator")
st.caption("Easily convert any folder/file structure into a Windows `.bat` file you can download and run.")

# Tabs for input method
tab1, tab2 = st.tabs(["✍️ Paste Structure", "📂 Upload File"])

structure_input = ""

with tab1:
    structure_input = st.text_area("Paste your folder structure here:", height=300, placeholder="MyProject/\n├── main.py\n├── requirements.txt\n└── src/\n    └── app.py")

with tab2:
    uploaded_file = st.file_uploader("Upload a `.txt` file containing the structure", type=["txt"])
    if uploaded_file:
        structure_input = uploaded_file.read().decode("utf-8")
        st.success("✅ File uploaded successfully!")

# Submit button
generate_btn = st.button("🚀 Generate Batch Script")

if generate_btn:
    if not structure_input.strip():
        st.error("❌ Please paste or upload a folder structure first.")
    else:
        bat_script, project_name = generate_bat(structure_input)

        if bat_script and project_name:
            st.success(f"✅ Batch script generated for project: **{project_name}**")
            with st.expander("📜 View Script", expanded=True):
                st.code(bat_script, language="bat")

            st.download_button(
                label=f"⬇️ Download {project_name}.bat",
                data=bat_script,
                file_name=f"{project_name}.bat",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.error("❌ Could not detect a root folder. Please ensure your structure starts with something like `MyProject/`.")
