def clear_message_bar(messagebar):
    """Deletes all messages in a message bar"""

    layout = messagebar.layout()
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            self.clear_layout(child.layout())
