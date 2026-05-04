# fmt: off
# since black formatter otherwise messes up the nice formatting of the regexes. 
# type: ignore
import re


"""
This is meant to mirror the frontend function to enforce url-format name uniqueness.

The frontend function:
export default function urlFormatter(value: string | number) {
	return String(value)
		.toLowerCase()
		.replace(/\s+/g, "-")
		.replace(/[åä]/g, "a")
		.replace(/ö/g, "o")
		.replace(/[^a-z0-9\-]/g, "") 
		.replace(/-+/g, "-")
		.replace(/^-|-$/g, "");
}
"""


def url_formatter(value: str | int) -> str:
    return (
        re.sub(r'^-|-$', '', 
        re.sub(r'-+', '-',
        re.sub(r'[^a-z0-9\-]', '',
        re.sub(r'[åä]', 'a',
        re.sub(r'ö', 'o',
        re.sub(r'\s+', '-',
        str(value).lower()
        ))))))
    )
