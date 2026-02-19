#include <QCoreApplication>
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQuickView>
#include <QString>
#include <QUrl>

int main(int argc, char *argv[]) {
  QGuiApplication *app = new QGuiApplication(argc, (char **)argv);
  app->setApplicationName("%%name%%.%%namespace%%");

  qDebug() << "Starting app from main.cpp";

  QQuickView *view = new QQuickView();
  view->setSource(QUrl("qrc:/qml/Main.qml"));
  view->setResizeMode(QQuickView::SizeRootObjectToView);
  view->show();

  return app->exec();
}