from flask import Flask, render_template_string, url_for ,request

app = Flask(__name__)

# Example payloads for host and guest
host_payload =  {
        "meetingNumber": 85496481286,
        "passWord": "lTbF8fVxGDbV7nz05dEq7Y4z8njkpL.1",
        "sdkKey": "OykU5axlQvWCpKw0EgJuAg",
        "signature": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZGtLZXkiOiJPeWtVNWF4bFF2V0NwS3cwRWdKdUFnIiwibW4iOjg1NDk2NDgxMjg2LCJyb2xlIjoxLCJpYXQiOjE3MjQyNzUyNjUsImV4cCI6MTcyNDI4MjQ2NSwiYXBwS2V5IjoiT3lrVTVheGxRdldDcEt3MEVnSnVBZyIsInRva2VuRXhwIjoxNzI0MjgyNDY1fQ.Asdhi-15bE2u9uCQxMDVpUuxxt0FIG4kqxHyg11fXxw",
        "userName": "interviewee"
    }

guest_payload = {
        "meetingNumber": 85496481286,
        "passWord": "lTbF8fVxGDbV7nz05dEq7Y4z8njkpL.1",
        "sdkKey": "OykU5axlQvWCpKw0EgJuAg",
        "signature": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZGtLZXkiOiJPeWtVNWF4bFF2V0NwS3cwRWdKdUFnIiwibW4iOjg1NDk2NDgxMjg2LCJyb2xlIjowLCJpYXQiOjE3MjQyNzUyOTcsImV4cCI6MTcyNDI4MjQ5NywiYXBwS2V5IjoiT3lrVTVheGxRdldDcEt3MEVnSnVBZyIsInRva2VuRXhwIjoxNzI0MjgyNDk3fQ.8PZL_R64CFS6spv5lpdyxCpOIhahbd7poQyBlUrxgnE",
        "userName": "candidate"
    }

@app.route('/')
def index():
    host_link = url_for('join_meeting', **host_payload)
    guest_link = url_for('join_meeting', **guest_payload)

    html_content = f"""
    <html>
    <body>
        <h1>Zoom Meeting Links</h1>
        <p><a href="{host_link}" target="_blank">Join as Host</a></p>
        <p><a href="{guest_link}" target="_blank">Join as Guest</a></p>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/join')
def join_meeting():
    meeting_number = request.args.get('meetingNumber')
    pass_word = request.args.get('passWord')
    sdk_key = request.args.get('sdkKey')
    signature = request.args.get('signature')
    user_email = request.args.get('userEmail')
    user_name = request.args.get('userName')

    html_content = f"""
    <html>
    <head>
        <!-- Load the necessary Zoom SDK libraries -->
        <script src="https://source.zoom.us/3.8.5/lib/vendor/react.min.js" defer></script>
        <script src="https://source.zoom.us/3.8.5/lib/vendor/react-dom.min.js" defer></script>
        <script src="https://source.zoom.us/3.8.5/lib/vendor/redux.min.js" defer></script>
        <script src="https://source.zoom.us/3.8.5/lib/vendor/redux-thunk.min.js" defer></script>
        <script src="https://source.zoom.us/3.8.5/lib/vendor/lodash.min.js" defer></script>
        <script src="https://source.zoom.us/3.8.5/zoom-meeting-3.8.5.min.js" defer></script>
    </head>
    <body>
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                ZoomMtg.setZoomJSLib('https://source.zoom.us/3.8.5/lib', '/av'); // Set the path for Zoom's JS libraries
                ZoomMtg.preLoadWasm();  // Preload WebAssembly files
                ZoomMtg.prepareWebSDK(); // Prepare the Web SDK

                ZoomMtg.init({{
                    leaveUrl: "https://zoom.us",
                    success: function() {{
                        console.log("Zoom SDK initialized successfully.");

                        ZoomMtg.join({{
                            sdkKey: "{sdk_key}",
                            signature: "{signature}",
                            meetingNumber: "{meeting_number}",
                            userName: "{user_name}",
                            passWord: "{pass_word}",
                            success: function(res) {{
                                console.log("Join meeting success:", res);
                            }},
                            error: function(res) {{
                                console.error("Join meeting error:", res);
                            }}
                        }});
                    }},
                    error: function(res) {{
                        console.error("Initialization of Zoom SDK failed:", res);
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == "__main__":
    app.run(port=5000)
