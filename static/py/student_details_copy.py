from browser import window, document, alert
    
hfmoon = window.halfmoon

# Temp var to store the current copied text
_text = ""

# {0} -> the text which was copied
success_alert_content = "'<code class='code font-size-16'>{0}</code>' was copied to your clipboard."
succes_alert_timeout = 3500

# {0} -> fail-reason.code
# {1} -> fail-reason.name
# {2} -> fail-reason.message
# {3} -> the text itself
failed_alert_content = "You browser may not support copying to clipboard.<code class='code'>({0}-{1} {2})</code>.\
                        You can copy manually by selecting and pressing <kbd>Crtl</kbd>+<kbd>C</kbd> below.\
                        <hr />\
                            <span class='d-flex justify-content-center'>\
                                <code class='code font-size-18'>{3}</code>\
                            </span>"
failed_alert_timeout = 15000

def on_copy_success(value):
    # print("Copied!", _text)

    hfmoon.initStickyAlert({
        'title': "Copied succesfully 🎉🎆",
        'content': success_alert_content.format(_text),
        'alertType': "alert-success",
        'fillType': "",
        'timeShown': succes_alert_timeout,
    })

def on_copy_failed(reason):
    # print("Not copied!", reason.code, reason.name, reason.message)
    
    hfmoon.initStickyAlert({
        'title': "Cannot Copy to clipboard",
        'content': failed_alert_content.format(reason.code, reason.name, reason.message, _text),
        'alertType': "alert-danger",
        'fillType': "",
        'timeShown': failed_alert_timeout,
    })

def python_copy(text):
    global _text
    _text = text
    window.navigator.clipboard.writeText(text).then(
        on_copy_success,
        on_copy_failed,
)

# Had to use this wierd name, as brython says that
# assigning window.foo = bar could introduce the
# risk of conflict with names defined in javascript

window.python_copy = python_copy