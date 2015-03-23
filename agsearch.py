import sublime, sublime_plugin
import subprocess, os

class AgSearchCommand(sublime_plugin.WindowCommand):
    def getProjectPaths(self, filename):
        # No valid filename
        if not filename or not os.path.isfile(filename):
            return None

        projectfolder = os.path.dirname(sublime.active_window().project_file_name())
        data = sublime.active_window().project_data()
        for folder in data["folders"]:
            path = os.path.join(projectfolder, folder["path"])
            if filename.startswith(path):
                return path
        return None

    def open(self, index):
        if index == -1:
            return
        if index >= len(self.locations):
            sublime.status_message("No more results")
            return
        self.currindex = index
        sublime.active_window().open_file(self.locations[index], sublime.ENCODED_POSITION)

    def run(self, type="word", input=""):
        print("AgSearch called")
        if type == "next":
            self.open(self.currindex+1)
            return
        window = sublime.active_window()
        dir = self.getProjectPaths(window.active_view().file_name())
        print(dir)
        if type ==  "word":
            view = window.active_view()
            word = view.substr(view.word(view.sel()[0]))
        if type == "input":
            window.show_input_panel("Search", "", lambda x: self.run("literal", x), None, None)
            return
        if type == "literal":
            word = input
        sublime.status_message("Searching for %s" % word)
        args=["ag", "-Q", "--noheading", "--numbers", "--nocolor", "--cc", "--hh"]
        args.append(word)
        wordlen = len(word)
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=dir)
        outs, _ = proc.communicate()
        lines = outs.decode().split("\n")
        self.results = []
        self.locations = []
        for line in lines:
            if line == "":
                continue
            print("-" + line + "-")
            file, linenum, search = line.split(":", 2)
            offset = search.find(word) + wordlen + 1
            self.locations.append(os.path.join(dir, file) + ":" + linenum + ":" + str(offset))
            self.results.append([search.strip(), file + ":" + linenum])
        print("Done")
        window.show_quick_panel(self.results, self.open)
