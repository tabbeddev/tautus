import Lomiri.Components 1.3
import Qt.labs.settings 1.0
import QtMultimedia 5.12
import QtQml 2.12
import QtQuick 2.7
// import Lomiri.Layouts 1.0
// import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import io.thp.pyotherside 1.5

Page {
    id: pageHome

    header: PageHeader {
        id: pageHeader
        title: i18n.tr("Home")
    }

    Column {
        anchors {
            top: pageHeader.bottom
        }

        Label {
            text: "Hello"
        }

        Label {
            text: "If you can see both this text and the text above, everything seems to work fine."
        }

    }
}
