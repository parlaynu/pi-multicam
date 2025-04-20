#pragma once

#include <QObject>
#include <QList>
#include <QString>
#include <QtQml>

#include <zenoh.hxx>


class ZenohSession : public QObject {
    Q_OBJECT
    QML_ELEMENT

    Q_PROPERTY(QList<QString> config READ config WRITE setConfig REQUIRED FINAL)

public:
    ZenohSession(QObject* parent=nullptr);
    virtual ~ZenohSession();

    const QList<QString>& config() const;
    void setConfig(const QList<QString>& config);

    Q_INVOKABLE zenoh::Session* session();

signals:
    void ready();

private:
    zenoh::Session* session_;
    QList<QString> config_;
};
