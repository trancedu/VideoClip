#include <QApplication>
#include <QWidget>
#include <QVBoxLayout>

#include <QMediaPlayer> 
#include <QVideoWidget>

class Widget : public QWidget
{
public:
    Widget(QWidget *parent = 0)
        : QWidget(parent)
    {
        QVBoxLayout *layout = new QVBoxLayout(this);
        QMediaPlayer *player = new QMediaPlayer(this);
        QVideoWidget *vw = new QVideoWidget;
        layout->addWidget(vw);
        player->setVideoOutput(vw);
        player->setMedia(QUrl::fromLocalFile("/Users/trance/Downloads/big_buck_bunny_720p_1mb.mp4"));
        player->setVolume(50);
        player->play();
    }
};

int main(int argc, char **argv)
{
    QApplication app(argc, argv);

    Widget widget;
    widget.resize(400, 300);
    widget.show();

    return app.exec();
}
