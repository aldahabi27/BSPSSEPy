"""Printing utility for BSPSSEPy Application
This module provides a function to print messages to the details_text_area
in the app"""

from __future__ import annotations
# from fun.bspssepy.app.bspssepy_print import append_to_details_text_area


def bspssepy_print(
    *args,
    app=None,
    _type: str | None = None,
    sep="\n",
    end=""
):
    """
    Prints messages to the details_text_area in the app if available.
    Falls back to printing in the terminal if no app is provided.

    This function automatically handles async execution using `call_later`
    when inside the GUI, so you don't have to use `await` explicitly.

    Parameters:
        *args: Variable number of arguments to print, similar to `print()`.
        app (BSPSSEPyApp, optional): The Textual app instance (default is
                                     None).
        _type (optional): If _type is ["d", "debug"], the message will only be
                          displayed if `app.debug_checkbox.value` is True.
        sep (str, optional): Separator used between arguments (default: space).
        end (str, optional): String appended at the end (default: newline).
    """
    # If no explicit app is provided but the last arg seems to be an app
    # instance, remove it from args and assign it to the app parameter.

    if not app and args and hasattr(args[-1], "bspssepy_application"):
        app = args[-1]
        args = args[:-1]

    # Join all arguments into a single string
    message = sep.join(map(str, args)) + end

    if app:
        if app.dummy_run:
            return
        if _type:
            # If debug_checkbox is checked, allow debug messages
            if _type.lower() in ["d", "debug"] and not app.debug_checkbox.value:
                return  # Skip debug messages if debugging is disabled

        append_to_details_text_area(app.details_text_area, message, app=app)

    else:
        # Fallback to terminal output when no GUI is available
        print(message)


def append_to_details_text_area(details_text_area, Message,app=None):
    """
    Appends a new message to the details_text_area without erasing previous content.

    Parameters:
        details_text_area (TextArea): The TextArea widget where the message should be added.
        Message (str): The message to append.
    """
    if details_text_area:
        if details_text_area.document.line_count > 5000:  # ✅ Prevents UI lag by clearing old messages
            details_text_area.clear()
            details_text_area.insert(text="[LOG CLEARED - TOO LONG]\n")


        # Append new text at the last line
        details_text_area.insert(
            text=f"{Message}",
            location=(details_text_area.document.line_count, 0),  # Move to last line
            maintain_selection_offset=True
        )

        if app:
            
            # def DetailsTextAreaSmartScroll (app: App, details_text_area):
            #     # Step 1: Move the cursor to the end of the details_text_area
            #     while not details_text_area.cursor_at_last_line:
            #         for i in range(5):
            #             app.call_later(details_text_area.action_cursor_page_down)
            #             app.call_later(details_text_area.action_cursor_line_end)
            #             print(f"CurrentCursorLoc={details_text_area.cursor_location}")
            #             print(f"contentheight = {details_text_area.content_size.height}")
            #         print(f"End? = {details_text_area.cursor_at_last_line}")
            #         break
            # DetailsTextAreaSmartScroll(app=app, details_text_area=details_text_area)
            app.call_later(details_text_area.scroll_end, animate=False, immediate=True)#, animate, False)  # Ensure latest message is visible
            # print(f"details_text_area.cursor_at_end_of_text = {details_text_area.cursor_at_end_of_text}")

            # print(f"")