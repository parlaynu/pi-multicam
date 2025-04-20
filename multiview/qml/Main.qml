import QtQuick
import QtQuick.Window
import QtQuick.Layouts
import parlaynu.zenoh 1.0


Window {
    id: root
    width: 1024
    height: 768

    required property int num_columns
    required property var key_expressions

    visible: true
    color: "black"

    Component.onCompleted: {
        root.showMaximized()
    }

    ZenohSession {
        id: zsession
        config: [
            "mode=\"peer\"",
            "listen/endpoints={\"peer\":[\"tcp/0.0.0.0:0\"]}",
            "transport/link/rx/buffer_size=4194304"
        ]
        onReady: console.log("session ready")
    }

    GridLayout {
        anchors.fill: parent
        columns: root.num_columns

        Repeater {
            model: root.key_expressions
            Viewer {
                required property string modelData

                Layout.fillWidth: true
                Layout.fillHeight: true

                session: zsession
                key_expression: modelData
            }
        }
    }
}
