import Lomiri.Components 1.3
import Qt.labs.settings 1.0
// import Lomiri.Layouts 1.0
// import QtQuick.Controls 2.2
// import QtQuick.Layouts 1.3
import QtMultimedia 5.12
import QtQml 2.12
import QtQuick 2.7
import io.thp.pyotherside 1.5

MainView {
    id: root

    property bool tablet: width >= units.gu(100)
    property Python pythonBridge

    objectName: 'mainView'
    applicationName: '%%name%%.%%namespace%%'
    automaticOrientation: true
    width: units.gu(45)
    height: units.gu(75)
    visible: true

    PageStack {
        id: nav

        anchors.fill: parent
        Component.onCompleted: {
            nav.push(Qt.resolvedUrl("pages/Home.qml"));
        }
    }

    Python {
        id: python

        Component.onCompleted: {
            python.setHandler("stdout", text => {
                console.log("python:", text)
            });

            python.addImportPath(Qt.resolvedUrl('../src/'));
            python.importModule_sync("main");
        }
    }

}
