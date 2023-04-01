#!/usr/bin/env python3

from os import listdir, mkdir
from os.path import isfile, join
from pathlib import Path
from zipfile import ZipFile
from tempfile import TemporaryDirectory
import json
import shutil

from xml.dom.minidom import getDOMImplementation, Document

COURSE_FILES = "./course_files"
OUTPUT_DIR = "./public"

type_describer = {
    0: "lesson",
    1: "exam",
}


def getDom():
    impl = getDOMImplementation()
    assert impl is not None
    dt = impl.createDocumentType(
        "html",
        "-//W3C//DTD XHTML 1.0 Strict//EN",
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
    )
    return impl.createDocument("http://www.w3.org/1999/xhtml", "html", dt)


def handle_content(i: int, content, dom, temp_dir: str, course_dir: str):
    t = type_describer[content["type"]]
    name: str = content["name"]

    if t == "exam":
        node_text = f"{i+1}-آزمون-{name}**"
        li = dom.createElement("li")
        li.appendChild(
            dom.createTextNode(node_text))
    else:
        node_text = f"{i+1}-{name}"
        src = join(temp_dir, content["filename"])
        dest_name = f"lesson_{i+1}.html"
        dest = join(
            course_dir, dest_name)
        shutil.copy2(src, dest)

        li = dom.createElement("li")
        a = dom.createElement("a")
        a.setAttribute("href", dest_name)
        li.appendChild(a)
        a.appendChild(
            dom.createTextNode(node_text))
    return li


def create_clear_output_dir(addr):
    shutil.rmtree(addr, ignore_errors=True)
    mkdir(addr)


def handle_course(course_path, output_dir):
    # full_out_dir = join(output_dir, TODO)
    # create_clear_output_dir(full_out_dir)

    with TemporaryDirectory() as temp_dir, ZipFile(course_path) as zipObject:
        zipObject.extractall(path=temp_dir)
        json_path = join(temp_dir, "Content.json")
        with open(json_path, "r", encoding="UTF-8") as json_file:
            json_obj = json.load(json_file)

            course_id = f"course_{json_obj['courseId']}"  # TODO
            course_dir = join(output_dir, course_id)
            output_html = join(course_dir, "index.html")

            print(course_id)
            create_clear_output_dir(course_dir)

            with open(output_html, "w", encoding="UTF-8") as my_index_html:
                dom = getDom()
                html = dom.documentElement
                ul = dom.createElement("ul")

                contents = sorted(
                    json_obj["contents"],
                    key=lambda a: int(a["contentorder"])
                )

                for i, content in enumerate(contents):
                    li = handle_content(i, content, dom, temp_dir, course_dir)
                    ul.appendChild(li)

                html.appendChild(ul)
                my_index_html.write(dom.toxml())


def main(courses_path, output_dir):

    for f in sorted(listdir(courses_path)):
        full_zip_path = join(courses_path, f)
        if not isfile(full_zip_path) or Path(full_zip_path).suffix != ".zip":
            continue

        handle_course(course_path=full_zip_path,
                      output_dir=output_dir)


if __name__ == "__main__":
    main(COURSE_FILES, OUTPUT_DIR)
