#pragma once

#include "z_session.h"

#include <QObject>
#include <QString>
#include <QVideoFrame>
#include <QVideoSink>
#include <QtQml>

#include <opencv2/opencv.hpp>
#include <zenoh.hxx>

#include <mutex>


class ZenohVideoPlayer : public QObject {
    Q_OBJECT
    QML_ELEMENT

    Q_PROPERTY(ZenohSession* session READ session WRITE setSession FINAL)
    Q_PROPERTY(QString keyExpression READ keyExpression WRITE setKeyExpression REQUIRED FINAL)
    Q_PROPERTY(QObject* videoOutput READ videoOutput WRITE setVideoOutput REQUIRED FINAL)

public:
    ZenohVideoPlayer(QObject* parent=nullptr);
    virtual ~ZenohVideoPlayer();

    ZenohSession* session();
    void setSession(ZenohSession* session);

    QString keyExpression() const;
    void setKeyExpression(const QString& key_expression);

    QObject* videoOutput();
    void setVideoOutput(QObject* voutput);

signals:
    void newFrame();

private slots:
    void onSample(const zenoh::Sample& sample);

private:
    void checkReady();

    cv::Mat decodePayload(const zenoh::Sample& s);

private:
    ZenohSession* session_;
    QString key_expression_;

    QObject* video_output_;
    QVideoSink* video_sink_;

    unsigned char* payload_;
    int payload_size_;
    cv::Mat image_;

    std::mutex cb_mux_;
};
