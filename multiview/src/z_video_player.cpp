#include "z_video_player.h"
#include <QDebug>


ZenohVideoPlayer::ZenohVideoPlayer(QObject* parent)
: QObject(parent),
  session_(nullptr),
  video_output_(nullptr),
  video_sink_(nullptr),
  payload_(nullptr),
  payload_size_(0)
{
}

ZenohVideoPlayer::~ZenohVideoPlayer()
{
    delete payload_;
}

ZenohSession* 
ZenohVideoPlayer::session()
{
    return session_;
}

void
ZenohVideoPlayer::setSession(ZenohSession* session)
{
    if (session_ != nullptr) {
        qFatal("session has already been set");
    }
    session_ = session;
    checkReady();
}

QString 
ZenohVideoPlayer::keyExpression() const
{
    return key_expression_;
}

void 
ZenohVideoPlayer::setKeyExpression(QString const& keyexpr)
{
    if (!key_expression_.isEmpty()) {
        qFatal("key expression already set to \"%s\"", key_expression_.toStdString().c_str());
    }
    key_expression_ = keyexpr;
    checkReady();
}

QObject*
ZenohVideoPlayer::videoOutput()
{
    return video_output_;
}

void
ZenohVideoPlayer::setVideoOutput(QObject* voutput)
{
    if (video_output_ != nullptr) {
        qFatal("video output has already been set");
    }

    auto *vsink = qobject_cast<QVideoSink *>(voutput);
    if (!vsink && voutput) {
        auto *mo = voutput->metaObject();
        mo->invokeMethod(voutput, "videoSink", Q_RETURN_ARG(QVideoSink *, vsink));
    }
    video_output_ = voutput;
    video_sink_ = vsink;

    checkReady();
}

void 
ZenohVideoPlayer::checkReady()
{
    if (session_ == nullptr || key_expression_.isEmpty() || video_output_ == nullptr || video_sink_ == nullptr) {
        return;
    }
    session_->session()->declare_background_subscriber(
        zenoh::KeyExpr(key_expression_.toStdString()),
        [this](const zenoh::Sample& sample) {
            this->onSample(sample);
        },
        zenoh::closures::none
   );
}

cv::Mat
ZenohVideoPlayer::decodePayload(const zenoh::Sample& sample)
{
    // get the payload and make sure the payload buffer is big enough
    auto& payload = sample.get_payload();
    if (payload.size() > payload_size_) {
        if (payload_) {
            delete payload_;
            payload_ = nullptr;
        }
        payload_size_ = static_cast<int>(1.5 * payload.size());
        payload_ = new unsigned char[payload_size_];
    }

    // copy the payload into the internal payload buffer
    auto reader = payload.reader();
    reader.read(payload_, payload.size());

    // wrap a Mat around the buffer - no copying done - so it can
    //   be used in the decode function,
    auto image_enc = cv::Mat(1, payload.size(), CV_8U, payload_);

    // decode the image. if the passed in `image_` is of the incorrect size,
    //   it is reallocated internally by imdecode.
    image_ = cv::imdecode(image_enc, cv::IMREAD_COLOR, &image_);

    return image_;
}

void
ZenohVideoPlayer::onSample(const zenoh::Sample& sample)
{
    // this method is called as a zenoh callback... protect it 
    //   as it might be called from multiple threads
    const std::lock_guard<std::mutex> lock(cb_mux_);

    // extract and decode the payload from the sample
    auto image = decodePayload(sample);

    // create and map the video frame so it's accessible
    QSize size(image.cols, image.rows);
    QVideoFrameFormat format(size, QVideoFrameFormat::Format_RGBX8888);
    QVideoFrame vframe(format);
    vframe.map(QVideoFrame::WriteOnly);

    // perform the color conversion directly into the video frame mapped memory
    cv::Mat dest(image.rows, image.cols, CV_8UC4, vframe.bits(0));
    cv:cvtColor(image, dest, cv::COLOR_BGR2RGBA);

    // unmap the video frame and display it
    vframe.unmap();

    video_sink_->setVideoFrame(vframe);
    emit newFrame();
}

