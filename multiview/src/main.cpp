#include "z_session.h"
#include "z_video_player.h"

#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QDebug>

#include <vector>
#include <string>
#include <iostream>
#include <CLI/CLI.hpp>


std::vector<std::string> parseCmdLine(int argc, char *argv[])
{
    CLI::App app{"Multicamera viewer"};
    argv = app.ensure_utf8(argv);

    std::vector<std::string> key_exprs;
    app.add_option("key_expr", key_exprs, "Key expressions to subscribe to (one per view)")->required();

    try {
        app.parse(argc, argv);
    } catch (const CLI::ParseError &e) {
        app.exit(e);
        return key_exprs;
    }

    return key_exprs;
}

static void registerQmlTypes()
{
    const char* uri = "parlaynu.zenoh";

    qmlRegisterModule(uri, 1, 0);
    qmlRegisterType<ZenohSession>(uri, 1, 0, "ZenohSession");
    qmlRegisterType<ZenohVideoPlayer>(uri, 1, 0, "ZenohVideoPlayer");
}

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);
    auto key_exprs = parseCmdLine(argc, argv);
    if (key_exprs.empty()) {
        return 1;
    }

    registerQmlTypes();

    QMap<QString, QVariant> properties;

    int columns = key_exprs.size() == 1 ? 1 :
                    key_exprs.size() <= 4 ? 2 : 3;

    properties["num_columns"] = QVariant::fromValue(columns);

    QList<QVariant> kexprs;
    for (const auto& v: key_exprs) {
        kexprs.append(QVariant::fromValue(QString::fromStdString(v)));
    }
    properties["key_expressions"] = kexprs;

    QQmlApplicationEngine engine;
    engine.setInitialProperties(properties);
    engine.load(QUrl("qrc:/Main.qml"));

    return app.exec();
}
