import javafx.application.Platform;
import javafx.beans.property.BooleanProperty;
import javafx.beans.property.DoubleProperty;
import javafx.beans.property.SimpleBooleanProperty;
import javafx.beans.property.SimpleDoubleProperty;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.scene.control.Button;
import javafx.scene.control.ProgressBar;
import java.io.InputStream;
import java.net.URL;

//each object of this class represents a table row
public class TableData {
    private  URL url;
    private final StringProperty fileName;
    private final StringProperty status = new SimpleStringProperty("Not Downloaded.");
    private final StringProperty buttonText = new SimpleStringProperty("Pause");
    private final DoubleProperty progress;
    private final SimpleBooleanProperty pauseDownload;
    private final SimpleBooleanProperty cancelDownload;
    private final BooleanProperty isButtonDisabled = new SimpleBooleanProperty(false);
    private final ProgressBar progressBar;
    private final Button pauseButton;
    private final Button cancelButton;
    private final InputStream inputStream;

    public TableData(URL url, String fileName, String status, double progress, InputStream inputStream) {
        this.url = url;
        this.fileName = new SimpleStringProperty(fileName);
        this.pauseDownload = new SimpleBooleanProperty(false);
        this.cancelDownload = new SimpleBooleanProperty(false);
        this.pauseButton = createPauseButton();
        this.cancelButton = createCancelButton();
        this.progress = new SimpleDoubleProperty(0.0);
        this.progressBar = createProgressBar();
        this.inputStream = inputStream;
    }

    public Button getPauseButton() {
        return pauseButton;
    }

    public Button getCancelButton() {
        return cancelButton;
    }

    private ProgressBar createProgressBar(){
        ProgressBar progressBar = new ProgressBar();
        progressBar.setVisible(false);
        progressBar.setPrefWidth(265);
        progressBar.setProgress(0);
        return progressBar;
    }

    private Button createPauseButton() {
        Button button = new Button("Pause");
        button.setVisible(false);
        button.setStyle("-fx-background-color: #5bb450; -fx-text-fill: #ffffff;");
        button.textProperty().bind(buttonTextProperty());
        Platform.runLater(() -> {


        button.setOnAction(event -> {
            setPauseDownload(!isPauseDownload());
            System.out.println(fileName.get()+" paused: "+isPauseDownload());
            buttonTextProperty().set(isPauseDownload()? "Resume" : "Pause");
        });
        });
        return button;
    }

    private Button createCancelButton() {
        Button button = new Button("Cancel");
        button.setStyle("-fx-background-color: #de0a26; -fx-text-fill: #ffffff;");
        button.setVisible(false);
        button.disableProperty().bind(isButtonDisabledProperty());
        Platform.runLater(() -> {
        button.setOnAction(event -> {
            isButtonDisabledProperty().set(true);
            pauseButton.setDisable(true);
            setCancelDownload(true);
            System.out.println(fileName.get()+" paused: "+isPauseDownload());
            setPauseDownload(false);
        });
        });
        return button;
    }

    public StringProperty buttonTextProperty(){
        return buttonText;
    }

    public BooleanProperty isButtonDisabledProperty(){
        return isButtonDisabled;
    }

    public URL getUrl() {
        return url;
    }

    public void setUrl(URL url) {
        this.url=url;
    }

    public String getFileName() {
        return fileName.get();
    }

    public void setFileName(String file) {
        this.fileName.set(file);
    }

    public String getStatus() {
        return status.get();
    }

    public void setStatus(String status) {
        this.status.set(status);
    }

    public StringProperty statusProperty(){
        return status;
    }

    public double getProgress() {
        return progress.get();
    }

    public DoubleProperty progressProperty() {
        return progress;
    }

    public ProgressBar getProgressBar() {
        return progressBar;
    }

    public void setProgress(double progress) {
        this.progress.set(progress);
    }

    public InputStream getInputStream() {
        return inputStream;
    }

    public boolean isPauseDownload() {
        return pauseDownload.get();
    }

    public void setPauseDownload(boolean value) {
        pauseDownload.set(value);;
    }

    public boolean isCancelDownload() {
        return cancelDownload.get();
    }

    public void setCancelDownload(boolean value) {
        cancelDownload.set(value);;
    }

}
