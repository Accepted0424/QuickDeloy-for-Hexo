import os
import re
import shutil
import subprocess
from os import makedirs
import tkinter as tk
from tkinter import filedialog, simpledialog


def get_user_input():
    def browse_hexo_project():
        # 打开文件夹选择对话框并显示选中的路径
        folder_path = filedialog.askdirectory(title="选择 Hexo 项目目录")
        hexo_entry.delete(0, tk.END)
        hexo_entry.insert(0, folder_path)

    def browse_md_file():
        # 打开文件选择对话框并显示选中的文件路径
        file_path = filedialog.askopenfilename(title="选择 Markdown 文件",
                                               filetypes=(("Markdown Files", "*.md"), ("All Files", "*.*")))
        md_entry.delete(0, tk.END)
        md_entry.insert(0, file_path)

    root = tk.Tk()
    root.title("Hexo 文章导入")

    hexo_label = tk.Label(root, text="Hexo项目路径:")
    hexo_label.grid(row=0, column=0, sticky="e", padx=10, pady=10)
    hexo_entry = tk.Entry(root, width=50)
    hexo_entry.grid(row=0, column=1, padx=10, pady=10)
    hexo_browse_button = tk.Button(root, text="浏览", command=browse_hexo_project)
    hexo_browse_button.grid(row=0, column=2, padx=10, pady=10)

    md_label = tk.Label(root, text="Markdown 文件路径:")
    md_label.grid(row=1, column=0, sticky="e", padx=10, pady=10)
    md_entry = tk.Entry(root, width=50)
    md_entry.grid(row=1, column=1, padx=10, pady=10)
    md_browse_button = tk.Button(root, text="浏览", command=browse_md_file)
    md_browse_button.grid(row=1, column=2, padx=10, pady=10)

    article_name_label = tk.Label(root, text="文章名称:")
    article_name_label.grid(row=2, column=0, sticky="e", padx=10, pady=10)
    article_name_entry = tk.Entry(root, width=50)
    article_name_entry.grid(row=2, column=1, padx=10, pady=10)

    config_label = tk.Label(root, text="Hexo主题配置文本:")
    config_label.grid(row=3, column=0, sticky="e", padx=10, pady=10)
    config_entry = tk.Text(root, height=5, width=50)  # 使用 Text 控件创建多行输入框
    config_entry.grid(row=3, column=1, padx=10, pady=10)

    submit_button = tk.Button(root, text="提交", command=root.quit)
    submit_button.grid(row=4, column=0, columnspan=3, pady=20)

    root.mainloop()
    return hexo_entry.get(), md_entry.get(), article_name_entry.get(), config_entry.get("1.0", tk.END).strip()


def create_image_folder(hexo_project_path, article_name):
    image_file_path = os.path.join(hexo_project_path, "source", "images", article_name)
    if not os.path.exists(hexo_project_path):
        os.makedirs(image_file_path)
    return image_file_path


def create_article_in_hexo(config, md_path, image_file_path_in_hexo, article_name):
    content = "---\n"
    content += config
    content += "\n"
    content += "---\n"
    with open(md_path, "r", encoding='utf-8') as f:
        article_content = f.read()
    content += article_content
    pattern = re.compile(r"\!\[.*\]\((.*)\)")
    matches = re.findall(pattern, content)
    for match in matches:
        image_path = match
        if not image_path.startswith(('http://', 'https://')):
            # 绝对路径替换为相对路径
            image_name = image_path.split("\\")[-1]
            relative_path_in_hexo = f"../images/{article_name}/{image_name}"
            content = content.replace(match, relative_path_in_hexo)
            # 复制图片到hexo目录下

            article_image_path = os.path.join(image_file_path_in_hexo)
            if not os.path.exists(article_image_path):
                os.makedirs(article_image_path)
            shutil.copy(image_path, article_image_path)

    md_path_in_hexo = os.path.join(hexo_project_path, "source", "_posts", article_name + ".md")
    with open(md_path_in_hexo, "w", encoding="utf-8") as f:
        f.write(content)


def deploy_hexo_article(hexo_project_path):
    git_bash_path = r"C:\Program Files\Git\bin\bash.exe"  # Git Bash 的默认路径
    if not os.path.exists(git_bash_path):
        print(f"Git Bash not found at {git_bash_path}. Please check your Git installation.")
        return

    os.chdir(hexo_project_path)

    try:
        # 生成静态文件
        subprocess.run([git_bash_path, "-c", "hexo g"], check=True)
        print("Hexo site generated successfully.")

        # 部署到远程服务器
        subprocess.run([git_bash_path, "-c", "hexo d"], check=True)
        print("Hexo site deployed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error during deployment: {e}")


try:
    hexo_project_path, md_path, article_name, config = get_user_input()
    image_file_path_in_hexo = create_image_folder(hexo_project_path, article_name)
    create_article_in_hexo(config, md_path, image_file_path_in_hexo, article_name)
    deploy_hexo_article(hexo_project_path)
except Exception as e:
    print(f"quit")
