#include <iostream>
#include <fstream>
#include <sstream>
#include <chrono>
#include <thread>
#include <ctime>
#include <syslog.h>
#include <unordered_map>
#include <filesystem>

using namespace std;
namespace fs = filesystem;

class ConfigManager {
public:
    ConfigManager(const string& configFile) : configFile_(configFile) {}

    bool readConfig() {
        ifstream file(configFile_);

        if (!file.is_open()) {
            cerr << "Error: Unable to open configuration file: " << configFile_ << endl;
            return false;
        }

        string line;
        while (getline(file, line)) {
            processConfigLine(line);
        }

        file.close();
        return true;
    }

    string getValue(const string& key) const {
        auto it = configMap_.find(key);
        return (it != configMap_.end()) ? it->second : "";
    }

private:
    void processConfigLine(const string& line) {
        istringstream iss(line);
        string key, value;

        if (getline(iss, key, '=') && getline(iss, value)) {
            trim(key);
            trim(value);
            configMap_[key] = value;
        }
    }

    void trim(string& str) {
        size_t start = str.find_first_not_of(" \t");
        size_t end = str.find_last_not_of(" \t");

        if (start != string::npos && end != string::npos)
            str = str.substr(start, end - start + 1);
        else
            str.clear();
    }

private:
    string configFile_;
    unordered_map<string, string> configMap_;
};

void backupFiles(const string& source, const string& destination) {
    fs::path sourcePath(source);
    fs::path destPath(destination);

    if (!fs::exists(sourcePath) || !fs::is_directory(sourcePath)) {
        cerr << "Error: Source directory does not exist or is not a directory." << endl;
        return;
    }

    if (!fs::exists(destPath)) {
        cerr << "Error: Destination directory does not exist." << endl;
        return;
    }

    auto now = chrono::system_clock::now();
    time_t now_c = chrono::system_clock::to_time_t(now);

    for (const auto& entry : fs::directory_iterator(sourcePath)) {
        if (fs::is_regular_file(entry.path())) {
            fs::path sourceFile = entry.path();
            fs::path destFile = destPath / (sourceFile.stem().string() + "_" + to_string(now_c) + sourceFile.extension().string());

            fs::copy_file(sourceFile, destFile, fs::copy_options::overwrite_existing);
        }
    }
}

void readConfig(const string& configFile, string& source, string& destination, string& frequency) {
    ConfigManager configManager(configFile);
    configManager.readConfig();

    source = configManager.getValue("SourceDirectory");
    destination = configManager.getValue("BackupDirectory");
    frequency = configManager.getValue("BackupFrequency");
}

void backupDaemon(const string& configFile) {
    string source, destination, frequency;

    while (true) {
        readConfig(configFile, source, destination, frequency);

        if (frequency == "every_2_minutes") {
            backupFiles(source, destination);

            openlog("BackupDaemon", LOG_PID, LOG_USER);
            syslog(LOG_INFO, "Backup completed every 2 minutes.");
            closelog();
        }

        this_thread::sleep_for(chrono::minutes(2));
    }
}

void controlDaemon(const string& configFile, const string& command) {
    if (command == "stop") {
        // Добавить код для завершения демона
        cout << "Stopping BackupDaemon..." << endl;
        // Пример: exit(0);
    } else if (command == "restart") {
        // Добавить код для перезапуска демона
        cout << "Restarting BackupDaemon..." << endl;
        // Пример: exit(0);
    } else if (command == "status") {
        // Добавить код для отображения статуса демона
        cout << "BackupDaemon is running." << endl;
    } else {
        cout << "Usage: ./BackupDaemon [stop|restart|status]" << endl;
    }
}

int main(int argc, char* argv[]) {
    if (argc == 2) {
        string configFile = "backup_config.ini";
        string command = argv[1];
        controlDaemon(configFile, command);
    } else {
        string configFile = "backup_config.ini";
        backupDaemon(configFile);
    }

    return 0;
}
