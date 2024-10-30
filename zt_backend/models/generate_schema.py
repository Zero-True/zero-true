from .api.request import (
    DependencyRequest,
    Request,
    ComponentRequest,
    DeleteRequest,
    CreateRequest,
    SaveRequest,
    ClearRequest,
    NotebookNameRequest,
    HideCellRequest,
    HideCodeRequest,
    NameCellRequest,
    ExpandCodeRequest,
    CellReactivityRequest,
    ShowTableRequest,
    ShareRequest,
    AddCommentRequest,
    DeleteCommentRequest,
    EditCommentRequest,
    ResolveCommentRequest,
    AddReplyRequest,
    DeleteReplyRequest,
    EditReplyRequest,
)
from .api.response import Response
from .notebook import Notebook, NotebookResponse, Dependencies, Dependency, Comment
from .components.slider import Slider
from .components.rating import Rating
from .components.file_input import FileInput
from .components.text_input import TextInput
from .components.text_area_input import TextArea
from .components.range_slider import RangeSlider
from .components.selectbox import SelectBox
from .components.button import Button
from .components.number_input import NumberInput
from .components.image import Image
from .components.text import Text
from .components.layout import Layout
from .components.autocomplete import Autocomplete
from .components.card import Card
from .components.timer import Timer
from .components.iframe import iFrame
from .components.html import HTML
import json


def generate_json(model, name):
    with open("zt_schema/" + name + ".json", "w+") as file:
        file.write(json.dumps(model.model_json_schema(), indent=2))


def generate_schema():
    generate_json(Request, "request")
    generate_json(ComponentRequest, "component_request")
    generate_json(DeleteRequest, "delete_request")
    generate_json(CreateRequest, "create_request")
    generate_json(SaveRequest, "save_request")
    generate_json(ClearRequest, "clear_request")
    generate_json(DependencyRequest, "dependency_request")
    generate_json(NotebookNameRequest, "notebook_name_request")
    generate_json(HideCellRequest, "hide_cell_request")
    generate_json(HideCodeRequest, "hide_code_request")
    generate_json(NameCellRequest, "name_cell_request")
    generate_json(ExpandCodeRequest, "expand_code_request")
    generate_json(CellReactivityRequest, "cell_reactivity_request")
    generate_json(ShowTableRequest, "show_table_request")
    generate_json(ShareRequest, "share_request")
    generate_json(Response, "response")
    generate_json(Notebook, "notebook")
    generate_json(NotebookResponse, "notebook_response")
    generate_json(Dependencies, "dependencies")
    generate_json(Dependency, "dependency")
    generate_json(Slider, "slider")
    generate_json(TextInput, "text_input")
    generate_json(TextArea, "text_area")
    generate_json(RangeSlider, "range_slider")
    generate_json(SelectBox, "select_box")
    generate_json(Text, "text")
    generate_json(Button, "button")
    generate_json(NumberInput, "number_input")
    generate_json(Image, "image")
    generate_json(Layout, "layout")
    generate_json(Autocomplete, "autocomplete")
    generate_json(Card, "card")
    generate_json(Text, "text")
    generate_json(Timer, "timer")
    generate_json(iFrame, "iframe")
    generate_json(HTML, "html")
    generate_json(Rating, "rating")
    generate_json(FileInput, "file_input")
    generate_json(Comment, "comment")
    generate_json(AddCommentRequest, "add_comment_request")
    generate_json(DeleteCommentRequest, "delete_comment_request")
    generate_json(EditCommentRequest, "edit_comment_request")
    generate_json(ResolveCommentRequest, "resolve_comment_request")
    generate_json(AddReplyRequest, "add_reply_request")
    generate_json(DeleteReplyRequest, "delete_reply_request")
    generate_json(EditReplyRequest, "edit_reply_request")
