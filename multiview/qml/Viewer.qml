import QtQuick
import QtMultimedia
import parlaynu.zenoh 1.0


Rectangle {
    id: viewer
    required property var session
    required property string key_expression

    Component.onCompleted: {
        console.log("key expression = ", key_expression)
    }

    color: "transparent"
    VideoOutput {
        id: voutput
        anchors.fill: parent
    }
    ZenohVideoPlayer {
        id: zsource
        session: viewer.session
        keyExpression: viewer.key_expression
        videoOutput: voutput
        onNewFrame: {
            console.log("player: received sample")
        }
    }
}
