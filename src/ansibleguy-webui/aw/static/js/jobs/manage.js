const ELEM_ID_TMPL_ROW2 = 'aw-api-data-tmpl-row2';
const ELEM_ID_TMPL_FIELD_TEXT = 'aw-api-data-tmpl-exec-text';
const ELEM_ID_TMPL_FIELD_CHOICES = 'aw-api-data-tmpl-exec-choices';
const ELEM_ID_TMPL_FIELD_CREDS = 'aw-api-data-tmpl-exec-creds';
const ELEM_ID_TMPL_FIELD_BOOL = 'aw-api-data-tmpl-exec-bool';
const ELEM_ID_TMPL_FIELD_VERB = 'aw-api-data-tmpl-exec-verbosity';
const EXEC_BOOL_FIELDS = ['mode_check', 'mode_diff'];
const PROMPT_SIMPLE_TYPES = ['tags', 'skip_tags', 'mode_check', 'mode_diff', 'limit', 'env_vars', 'cmd_args', 'verbosity', 'credentials'];
const PROMPT_SEPARATOR = ';';
const PROMPT_ARG_SEPARATOR = '#';
const PROMPT_CHOICE_SEPARATOR = ',';
const PROMPT_ENFORCE = 'enforce';
const PROMPT_LIMIT = 'limit';
const PROMPT_LIMIT_REQUIRE = 'limit_req';
const PROMPT_META_FIELDS = [PROMPT_ENFORCE, PROMPT_LIMIT_REQUIRE];
const PROMPT_SIMPLE_NAMES = [];
PROMPT_SIMPLE_NAMES['tags'] = 'Tags';
PROMPT_SIMPLE_NAMES['skip_tags'] = 'Skip Tags';
PROMPT_SIMPLE_NAMES['mode_check'] = 'Check Mode';
PROMPT_SIMPLE_NAMES['mode_diff'] = 'Difference Mode';
PROMPT_SIMPLE_NAMES[PROMPT_LIMIT] = 'Limit';
PROMPT_SIMPLE_NAMES['env_vars'] = 'Environmental Variables';
PROMPT_SIMPLE_NAMES['cmd_args'] = 'CLI Arguments';
PROMPT_SIMPLE_NAMES['verbosity'] = 'Verbosity';
PROMPT_SIMPLE_NAMES['credentials'] = 'Credentials';
const ATTR_BTN_QUICK_EXEC = 'aw-quick-exec';


function buildExecutionFields(promptsSerialized) {
    let prompts = [];

    if (is_set(promptsSerialized)) {
        for (field of promptsSerialized.split(PROMPT_SEPARATOR)) {
            let tmplElem = ELEM_ID_TMPL_FIELD_TEXT;

            if (PROMPT_META_FIELDS.includes(field)) {
                continue;

            } else if (PROMPT_SIMPLE_TYPES.includes(field)) {
                let name = PROMPT_SIMPLE_NAMES[field];

                if (EXEC_BOOL_FIELDS.includes(field)) {
                    tmplElem = ELEM_ID_TMPL_FIELD_BOOL;
                } else if (field == 'verbosity') {
                    tmplElem = ELEM_ID_TMPL_FIELD_VERB;
                } else if (field == 'credentials') {
                    tmplElem = ELEM_ID_TMPL_FIELD_CREDS;
                }
                let fieldHtml = document.getElementById(tmplElem).innerHTML;
                fieldHtml = fieldHtml.replaceAll('${PRETTY}', name);
                fieldHtml = fieldHtml.replaceAll('${FIELD}', field);
                if (field == PROMPT_LIMIT  && promptsSerialized.includes(PROMPT_LIMIT_REQUIRE)) {
                    fieldHtml = fieldHtml.replaceAll('${attrs}', 'required');
                } else {
                    fieldHtml = fieldHtml.replaceAll('${attrs}', '');
                }
                prompts.push(fieldHtml);

            } else {
                let fields = field.split(PROMPT_ARG_SEPARATOR);
                let name = fields[0];
                let varName = fields[1];
                let kind = fields[2];
                let required = fields[3];
                let choices = fields[4];
                let regex = fields[5];

                let attrs = '';
                if (is_set(regex)) {
                    regex = atob(regex);
                    attrs = 'pattern="' + regex + '" '
                }
                if (required == '1') {
                    attrs += 'required';
                }

                if (kind == 'dropdown') {
                    tmplElem = ELEM_ID_TMPL_FIELD_CHOICES;
                }

                let fieldHtml = document.getElementById(tmplElem).innerHTML;
                fieldHtml = fieldHtml.replaceAll('${PRETTY}', name);
                fieldHtml = fieldHtml.replaceAll('${FIELD}', 'var=' + varName);
                if (is_set(attrs)) {
                    fieldHtml = fieldHtml.replaceAll('${attrs}', attrs);
                }

                if (kind == 'dropdown' && is_set(choices)) {
                    let options = [];
                    for (choice of choices.split(PROMPT_CHOICE_SEPARATOR)) {
                        options.push('<option value="' + choice + '">' + choice + '</option>');
                    }
                    fieldHtml = fieldHtml.replaceAll('${OPTIONS}', options.join(''));
                }

                prompts.push(fieldHtml);
            }
        }
    }

    return prompts;
}

function updateApiTableDataJob(row, row2, entry) {
    // job
    row.innerHTML = document.getElementById(ELEM_ID_TMPL_ROW).innerHTML;
    row.cells[0].innerText = entry.name;
    row.cells[1].innerText = entry.inventory_file;
    row.cells[2].innerText = entry.playbook_file;

    if (entry.comment == "") {
        row.cells[3].innerText = '-';
    } else {
        row.cells[3].innerText = entry.comment;
    }
    if (entry.schedule == "") {
        row.cells[4].innerText = '-';
    } else {
        let scheduleHtml = entry.schedule;
        if (!entry.enabled) {
            scheduleHtml += '<br><i>(disabled)</i>';
        }
        row.cells[4].innerHTML = scheduleHtml;
    }

    if (entry.executions.length == 0) {
        var lastExecution = null;
        row.cells[5].innerText = '-';
        row.cells[6].innerText = '-';
    } else {
        var lastExecution = entry.executions[0];
        row.cells[5].innerHTML = shortExecutionStatus(lastExecution);

        if (entry.next_run == null) {
            row.cells[6].innerText = '-';
        } else {
            row.cells[6].innerText = entry.next_run;
        }
    }

    let actionsTemplate = document.getElementById(ELEM_ID_TMPL_ACTIONS).innerHTML;
    actionsTemplate = actionsTemplate.replaceAll('${ID}', entry.id);
    if (lastExecution != null) {
        actionsTemplate = actionsTemplate.replaceAll('${EXEC_ID_1}', lastExecution.id);
    } else {
        actionsTemplate = actionsTemplate.replaceAll('${EXEC_ID_1}', 0);
    }
    if (is_set(entry.execution_prompts) && entry.execution_prompts.includes(PROMPT_ENFORCE)) {
        actionsTemplate = actionsTemplate.replaceAll('${disable}', 'disabled');
    } else {
        actionsTemplate = actionsTemplate.replaceAll('${disable}', '');
    }

    row.cells[7].innerHTML = actionsTemplate;

    // custom execution
    row2.setAttribute("id", "aw-spoiler-" + entry.id);
    row2.setAttribute("hidden", "hidden");
    let execTemplate = document.getElementById(ELEM_ID_TMPL_ROW2).innerHTML;
    execTemplate = execTemplate.replaceAll('${ID}', entry.id);
    row2.innerHTML = execTemplate;
    let prompts = buildExecutionFields(entry.execution_prompts);

    let execForm = document.getElementById('aw-job-exec-' + entry.id);
    execForm.innerHTML = prompts.join('<br>') + execForm.innerHTML;
    execForm.addEventListener('submit', function(e) {
        e.preventDefault();
        customExecution(this.elements);
    })
}

function customExecution(formElements) {
    let data = {};
    let cmdArgs = '';
    let job_id = undefined;
    for (elem of formElements) {
        if (elem.hasAttribute('name')) {
            if (elem.name == 'job_id') {
                job_id = elem.value;
            } else if (elem.name.startsWith('var')) {
                let varName = elem.name.split('=')[1];
                cmdArgs += ' -e "' + varName + '=' + elem.value + '"';
            } else if (elem.name == 'credentials') {
                if (elem.value.startsWith('global_')) {
                    data['credential_global'] = elem.value.split('_')[1];
                } else {
                    data['credential_user'] = elem.value.split('_')[1];
                }
            } else {
                data[elem.name] = elem.value;
            }
        }
    }
    if ('cmd_args' in data) {
        cmdArgs += data['cmd_args'];
    }
    data['cmd_args'] = cmdArgs;

    $.ajax({
        type: "post",
        url: "/api/job/" + job_id,
        data: data,
        success: function (result) { apiActionSuccess(result); },
        error: function (result, exception) { apiActionError(result, exception); },
    });

}

function switchQuickExecution($this) {
    let btn = document.getElementById($this.attr(ATTR_BTN_QUICK_EXEC));
    if (btn.disabled === true) {
        btn.disabled = false;
    } else {
        btn.disabled = true;
    }
}

$( document ).ready(function() {
    apiEndpoint = "/api/job?executions=true&execution_count=1";
    fetchApiTableData(apiEndpoint, updateApiTableDataJob, true);
    setInterval('fetchApiTableData(apiEndpoint, updateApiTableDataJob, true)', (DATA_REFRESH_SEC * 1000));
    $('.aw-main').on('click', '.aw-btn-custom-execution', function() {
        switchQuickExecution(jQuery(this));
    })
});
