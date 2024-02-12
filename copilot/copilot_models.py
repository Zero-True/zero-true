from pydantic import BaseModel, Field
from typing import List
from typing_extensions import Literal

class BlankRequest(BaseModel):
    # Add fields if the signInInitiate request needs any parameters
    pass

class SignInConfirmRequest(BaseModel):
    userCode: str  # Assuming signInConfirm requires a userCode field

class TextDocumentItem(BaseModel):
    uri: str
    languageId: str
    version: int
    text: str

class DidOpenTextDocumentParams(BaseModel):
    textDocument: TextDocumentItem

class Position(BaseModel):
    line: int
    character: int

class DocumentItem(BaseModel):
    version: int
    position: Position
    uri: str

class GetCompletionsParams(BaseModel):
    doc: DocumentItem


class VersionedTextDocumentIdentifier(BaseModel):
    uri: str
    version: int

class TextDocumentContentChangeEvent(BaseModel):
    text: str  # The new text of the whole document

class DidChangeTextDocumentParams(BaseModel):
    textDocument: VersionedTextDocumentIdentifier
    contentChanges: List[TextDocumentContentChangeEvent] = Field(default_factory=list)


class CopilotPayloadSignInInitiate(BaseModel):
    verificationUri: str
    status: str
    userCode: str
    expiresIn: int
    interval: int

class CopilotPayloadSignInConfirm(BaseModel):
    status: Literal["AlreadySignedIn", "MaybeOk", "NotAuthorized", "NotSignedIn", "OK"]
    user: str

class CopilotPayloadSignOut(BaseModel):
    status: Literal["NotSignedIn"]


class Position(BaseModel):
    line: int
    character: int

class Range(BaseModel):
    start: Position
    end: Position

class Completion(BaseModel):
    text: str
    position: Position
    uuid: str
    range: Range
    displayText: str

class CopilotGetCompletionsResult(BaseModel):
    completions: List[Completion]

class AcceptRequest(BaseModel):
    uuid: str

class RejectRequest(BaseModel):
    uuid: str