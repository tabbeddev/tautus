import Lomiri.Components 1.3
import Qt.labs.settings 1.0
import QtMultimedia 5.12
import QtQml 2.12
import QtQuick 2.7
// import Lomiri.Layouts 1.0
// import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import io.thp.pyotherside 1.4

Page {
    id: pageHome

    // We passed down the Python-Object to this page if you want to use it
    property Python pythonBridge

    // Use the deprecated title property instead of header, as header messes up the page size
    title: i18n.tr("Home")

    Column {
        Label {
            text: "Hello"
        }

        Label {
            text: "If you can see both this text and the text above, everything seems to work fine."
        }

    }

}
