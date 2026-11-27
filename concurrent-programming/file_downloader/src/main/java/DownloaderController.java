import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.collections.transformation.FilteredList;
import javafx.concurrent.Task;
import javafx.concurrent.WorkerStateEvent;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.layout.HBox;
import javafx.stage.DirectoryChooser;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import javafx.application.Platform;

public class DownloaderController {

    @FXML
    private TextField urlTextField, directoryPathField;
    @FXML
    private Button downloadButton, directoryButton, addButton;
    @FXML
    private Label downloaded;
    @FXML
    private TableView<TableData> table;
    @FXML
    private TableColumn<TableData, String> fileColumn, statusColumn;
    @FXML
    private TableColumn<TableData, Double> progressColumn;
    private Task<Void> downloadTask;
    private Set<String> urlSet = new HashSet<>();
    private ObservableList<TableData> tableDataList = FXCollections.observableArrayList();
    private FilteredList<TableData> filteredData = new FilteredList<>(
            tableDataList,
            urlData -> tableDataList.indexOf(urlData) < MAX_ITEMS
    );
    private File selectedDirectory;
    private static int finishedDownloads = 0;
    private static int allDownloads = 0;
    private static int canceledDownloads = 0;
    private static final int MAX_ITEMS = 10;
    private static boolean isConnected = true;
    
    /*----------------------------Part 1: Initializing the TableView--------------------------------------*/
    //method to initialize the table where the added files are going to be listed
    public void initialize() {
        setUpFileColumn();
        setUpStatusColumn();
        setUpProgressColumn();


        progressColumn.setPrefWidth(406);
        table.setItems(filteredData);
    }
    
    //method to initialize the File Name column in the TableView
    private void setUpFileColumn(){
        fileColumn.setReorderable(false);
        fileColumn.setResizable(false);
        fileColumn.setCellValueFactory(new PropertyValueFactory<>("fileName"));
    }
    
    //method to initialize the Download Status column in the TableView
    private void setUpStatusColumn(){
        statusColumn.setReorderable(false);
        statusColumn.setResizable(false);
        statusColumn.setCellValueFactory(new PropertyValueFactory<>("status"));
        statusColumn.setCellFactory(this::downloadStatus);
    }
    
    //method to take care of updating the download status column of the table
    private TableCell<TableData, String> downloadStatus(TableColumn<TableData, String> column) {
        return new TableCell<TableData, String>() {
            private final Label label = new Label();

            @Override
            protected void updateItem(String item, boolean empty) {
                super.updateItem(item, empty);

                if (empty || item == null) {
                    setGraphic(null);
                } else {
                    TableData urlData = getTableView().getItems().get(getIndex());
                    {
                        label.textProperty().bind(urlData.statusProperty());
                        setGraphic(label);
                    }
                }
            }
        };
    }
    
    //method to initialize the Progress column in the TableView
    private void setUpProgressColumn() {
        progressColumn.setReorderable(false);
        progressColumn.setResizable(false);
        progressColumn.setCellValueFactory(new PropertyValueFactory<>("progress"));
        progressColumn.setCellFactory(param -> new TableCell<TableData, Double>() {
            private final HBox hbox = new HBox();

            {
                hbox.setSpacing(5);
                setGraphic(hbox);
            }

            @Override
            protected void updateItem(Double progress, boolean empty) {
                super.updateItem(progress, empty);
                if (empty || progress == null) {
                    hbox.getChildren().clear();
                } else {
                    TableData data = getTableRow().getItem();

                    ProgressBar progressBar = data.getProgressBar();
                    Button pauseButton = data.getPauseButton();
                    Button cancelButton = data.getCancelButton();

                    if (!hbox.getChildren().contains(progressBar)) {
                        hbox.getChildren().addAll(progressBar, pauseButton, cancelButton);
                    }

                    // Update the progress bar value
                    progressBar.setProgress(progress);
                }
            }
        });
    }


    /*----------------------------Part 2: Handling Directory Choosing--------------------------------------*/
    //method to handle the browse button action
    @FXML
    protected void handleChooseDirectory(ActionEvent event) {
        //DirectoryChooser object to use a directory chooser dialog
        DirectoryChooser directoryChooser = new DirectoryChooser();
        //setting the title of the directory chooser dialog
        directoryChooser.setTitle("Select Download Directory");
        //storing the selected directory in the respective variable for it
        selectedDirectory = directoryChooser.showDialog(downloadButton.getScene().getWindow());

        //displaying the directory's path in its respective textfield
        if (selectedDirectory != null) {
            directoryPathField.setText(selectedDirectory.getAbsolutePath());
        }
    }

    /*----------------------------Part 3: Handling Adding to the TableView--------------------------------------*/
    //method to handle the add button action
    @FXML
    protected void handleAdd(ActionEvent event) {
        System.out.println("\nAdding...");
        if(!validateTextField()){
            return;
        }

        if(urlSet.contains(urlTextField.getText())){
            Platform.runLater(() -> {
                showAlert(Alert.AlertType.WARNING, "Warning", "URL already exists.", "This URL is already added.");
            });
            return;
        }

        int nbr = table.getItems().size();
        if (nbr < MAX_ITEMS) {
            String url = urlTextField.getText();
            addButton.setDisable(true);
            Task<Void> urlCheckTask = createURLCheckTask(url, nbr);

            new Thread(urlCheckTask).start();
        } else {
            showAlert(Alert.AlertType.ERROR, "Error", "Can't add URL.", "You reached the max number of added URLs (10 URLs)");
            urlTextField.setText(null);
        }
    }
    
    //method to check the URL Text Field before adding it
    private boolean validateTextField(){
        if(urlTextField.getText() != null && !urlTextField.getText().trim().isEmpty()){
            if (!(urlTextField.getText().trim().startsWith("https://") || urlTextField.getText().startsWith("http://"))){
                Platform.runLater(() -> {
                    showAlert(Alert.AlertType.ERROR, "Error", "Can't add URL.", "URL must start with \"https://\" or \"http://\".");
                });
                return false;
            }
        }else{
                Platform.runLater(() -> {
                    showAlert(Alert.AlertType.ERROR, "Error", "Empty URL field.", "Enter a URL, please.");
                });
                return false;
            
        }
        return true;
    }
    
    //method to create a Task that handles the validation of the URL and its adding
    private Task<Void> createURLCheckTask(String url, int nbr){
        return new Task<Void>() {
                @Override
                protected Void call() throws Exception {
                    try {
                        URI uri = new URI(url.trim());
                        URL url2 = uri.toURL();
                        
                        InputStream inputStream = url2.openStream();
                        
                        //splitting the components of the retrieved URL in an array
                        String[] paths = url.split("/");
                        //getting the last component (file name) of the URL
                        String filename = paths[paths.length - 1];
                        TableData data = new TableData(url2, filename, "Not Downloaded", 0.0, inputStream);
                        urlSet.add(urlTextField.getText());
                        Platform.runLater(() -> {
                            tableDataList.add(data);
                            urlTextField.setText(null);
                            System.out.println("\nRows = " + (nbr + 1));
                            System.out.println("\npause:" +data.isPauseDownload()+"\ncancel:" +data.isCancelDownload());
                            
                        });
                    } catch (URISyntaxException | IOException e) {
                            Platform.runLater(() -> {
                            showAlert(Alert.AlertType.ERROR, "Error", "Can't add URL.", "Invalid URL or bad connection. Please, check and retry.");
                        });
                    
                    }finally {
                        addButton.setDisable(false);
                    }
                    return null;
                }
            };
    }

    /*----------------------------Part 3: Handling the Concurrent Download--------------------------------------*/
    //method to handle the download all button action
    @FXML
    protected void handleDownload(ActionEvent event) {
        if(checkConditions()){
            download();
        } 
    }
    
    //method to verify some conditions before starting the download
    private boolean checkConditions(){
        //checking if at least one file is added to download it
        if(table.getItems().size()==0){
            //if no files are added, show an alert window to notify that at least one file should be added
            showAlert(Alert.AlertType.ERROR, "Error", "Can't download.", "Please add at least one URL first.");
            return false;
        }

        //checking if a directory is selected
        if (selectedDirectory == null) {
            //if not selected, show an alert window to notify that a directory should be selected
            showAlert(Alert.AlertType.ERROR, "Error", "Can't start download.", "Please choose a download directory.");
            return false;
        }

        if (!checkConnection(table.getItems().get(0).getUrl())) {
                // Additional handling code here... 
                return false;
        }
        return true;
    }
    
    //method that handles the concurrent download
    private void download(){
        //creating a thread pool
        ExecutorService executor = Executors.newFixedThreadPool(8);
        for (TableData urlData : table.getItems()) {
            //method to display the progress bar and the pause / cancel buttons
            setUpFileDownloadUI(urlData);
            //creating a Task that will take care of the download
            downloadTask = createDownloadTask(urlData);               
            urlData.progressProperty().bind(downloadTask.progressProperty());
            urlData.statusProperty().bind(downloadTask.messageProperty());
            //event handler when the downloadTask fails
            downloadTask.setOnFailed(this::onDownloadFailed);
            //submitting the downloadTask to the thread pool
            executor.submit(downloadTask);
        }
        //handler when the downloadTask is suuccessful
        downloadTask.setOnSucceeded(this::onDownloadSucceeded);
        //after all files got their proper tasks, the thread pool doesn't allow any more submitted tasks
        executor.shutdown();
    }
    
    //method to add to the ui the progress bars and pause/cancel buttons related to each download operation
    private void setUpFileDownloadUI(TableData urlData){
            urlData.getProgressBar().setVisible(true);
            urlData.getPauseButton().setVisible(true);
            urlData.getCancelButton().setVisible(true);
    }
    
    //method to create a Download Task that represents the download process
    private Task<Void> createDownloadTask(TableData urlData){
        return new Task<Void>(){
            //Overriding the call method to use it when the task starts running
                @Override
                protected Void call() throws Exception {
                    try {
                        updateMessage("Waiting...");
                        //making Changes in the GUI
                        Platform.runLater(() -> {
                            changeGUI();
                        });

                        InputStream inputStream = urlData.getInputStream();
                        File newFile = new File(selectedDirectory, urlData.getFileName());
                        //creating a FileOutputStream to write the downloaded data to a file, named filename, in the previously selected directory
                        FileOutputStream fileOutputStream = new FileOutputStream(newFile);

                        //variables to track the total number of bytes read during the download operation
                        AtomicInteger totalRead = new AtomicInteger(0);
                        int read;

                        //array to store the read and to be written data
                        byte[] bytes = new byte[8192];

                        //variable to store the size in bytes of the to be written data
                        int len ;

                        //variable to store the total size of the file
                        double fileSize = getFileSize(urlData.getUrl());
                    
                        System.out.println(fileSize);
                        LocalDateTime lastConnectionCheck = LocalDateTime.now();
                        boolean check = true;
                       double progress = 0;
                        //start of reading and writing orepation
                        while (progress != 1) {
                            
                            if(ChronoUnit.SECONDS.between(lastConnectionCheck, LocalDateTime.now())>= 60){
                                check = checkConnection(urlData.getUrl());
                                lastConnectionCheck = LocalDateTime.now();
                                System.out.println("\nconnection: "+check);  
                            }
                            if(check){
                                
                                if(urlData.isPauseDownload()){
                                    System.out.println("Pause detected.");
                                    updateMessage("Paused");
                                    while(urlData.isPauseDownload()){
                                        Thread.sleep(1000);
                                        
                                    }
                                    System.out.println("Resume detected.");
                                    updateMessage("Downloading...");
                                }
                                if(urlData.isCancelDownload()){
                                    updateMessage("Canceled.");
                                    System.out.println("Cancel detected");
                                    fileOutputStream.close();
                                    inputStream.close();
                                    while(newFile.exists()){
                                        

                                        System.out.println("Deleting..");
                                        newFile.delete();
                                    }
                                    System.out.println("Deleted");
                                    
                                    Thread.currentThread().interrupt();
                                    System.out.println("task interrupted");
                                    canceledDownloads++;
                                    allDownloads++;
                                    return null;
                                }
                                if((len = inputStream.read(bytes)) != -1){
                                fileOutputStream.write(bytes, 0, len);
                                }else{
                                    break;
                                }
                                
                                read = totalRead.addAndGet(len);
//                                System.out.println(read+" bytes read");
                                //calculate the current progress of the download
                                progress = read / fileSize;

                                updateProgress(progress, 1);
//                                System.out.println("Progress updated");
                                double finalProgress = progress;
                                    updateMessage("Downloading...("+(int)(finalProgress *100)+"%)");
//                                System.out.println("message updated");
                            
                                if(progress == 1){
                                    updateMessage("Completed.");
                                }
                            }   
                            
                              
                        }
                        Thread.sleep(10);
                        finishedDownloads++;
                        allDownloads++;
                        fileOutputStream.close();
                        inputStream.close();
                    } catch (IOException e) {
                        e.printStackTrace();
                        throw e;
                    }
                        return null;
                }
            };
    }
    
    //method to specify what happens when a downloadTask fails
    private void onDownloadFailed(WorkerStateEvent event){
        Platform.runLater(() -> {showAlert(Alert.AlertType.ERROR, "Error", "Download failed", "Please retry.");
                    resetStage();
        });
    }
    
    //method to specify what happens when a downloadTask is successful
    private void onDownloadSucceeded(WorkerStateEvent event) {
        while (allDownloads != table.getItems().size()){

        }
        //show an alert window to notify that the download is successful
        showAlert(Alert.AlertType.INFORMATION, "Success", "Downloads completed", "Total number of files: "+allDownloads+"\nDownloaded: "+finishedDownloads+"\nCancelled: "+canceledDownloads);
        resetStage();
    }
    
    //method to retrieve the file's size
    private long getFileSize(URL url) {
        try {
            return url.openConnection().getContentLengthLong();
        } catch (Exception e) {
            e.printStackTrace();
            Platform.runLater(() -> showAlert(Alert.AlertType.ERROR, "Error", "Failed to get file size", e.getMessage()));
            return -1;
        }
    }
    
    //method to check the connection to the URL
    private boolean checkConnection(URL url) {
       try {
            
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setConnectTimeout(5000); // Set a timeout
            connection.connect();
            int responseCode = connection.getResponseCode();
            if (responseCode != HttpURLConnection.HTTP_OK) {
                throw new IOException("Failed to connect to the URL");
            }
            isConnected = true;
            return true;
        } catch (IOException  e) {
            if(isConnected){
                Platform.runLater(() -> {
                        showAlert(Alert.AlertType.ERROR, "Error", "Lost connection.", "Check you connection and retry.");
                });
            }
            isConnected=false;
             System.out.println("A connection error occurred: " + e.getMessage());
             return false;
        }
    }

    /*----------------------------Part 4: More UI contol --------------------------------------*/
    //method to change the GUI during the download
    private void changeGUI(){
        directoryButton.setDisable(true);
        downloadButton.setDisable(true);
        addButton.setDisable(true);
        table.refresh();
    }

    //method to take care of resetting the GUI after the download
    private void resetStage(){
        tableDataList.clear();
        downloadButton.setDisable(false);
        directoryButton.setDisable(false);
        addButton.setDisable(false);
        finishedDownloads=0;
        allDownloads=0;
        canceledDownloads=0;
        urlSet.clear();
    }

    //method to take care of creating the alerts and displaying them
    private void showAlert(Alert.AlertType alertType, String title, String header, String content) {
        Alert alert = new Alert(alertType);
        alert.setTitle(title);
        alert.setHeaderText(header);
        alert.setContentText(content);
        alert.showAndWait();
    }
  
}

