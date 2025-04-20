#include "z_session.h"
#include <QRegularExpression>


ZenohSession::ZenohSession(QObject* parent)
: QObject(parent),
  session_(nullptr)
{
}

ZenohSession::~ZenohSession()
{
    if (session_) {
        session_->close();
    }
}

const QList<QString>&
ZenohSession::config() const
{
    return config_;
}

void
ZenohSession::setConfig(const QList<QString>& overrides)
{
    // copy the config settings
    config_.append(overrides);

    // update the default config values
    zenoh::ZResult err;
    zenoh::Config config = zenoh::Config::create_default();
    QRegularExpression re("(.*?)=(.*)");
    for (auto it = config_.begin(); it != config_.end(); ++it) {
        auto match = re.match(*it);
        if (!match.hasMatch()) {
            qFatal("no match for %s", it->toStdString().c_str());
        }
        auto key = match.captured(1);
        auto value = match.captured(2);
        qInfo() << key << "=" << value;
        config.insert_json5(key.toStdString(), value.toStdString(), &err);
        if (err != 0) {
            qFatal("insert_json5 failed for: %s = %s with %d", key.toStdString().c_str(), value.toStdString().c_str(), err);
        }
    }

    // create the session
    session_ = new zenoh::Session(std::move(config));

    // notify everyone that we're ready
    emit ready();
}

zenoh::Session*
ZenohSession::session()
{
    return session_;
}

