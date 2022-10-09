$("#btn-refresh").click(function() {
  $("#table").bootstrapTable("refresh", {});
});

function actionsFormatter(value, row, index) {
  return [
    '<a class="task-view mr-3" href="' + run_logs_url + '?id=' + row.id + '" title="View">',
    '<i class="fa fa-list" style="color: #858796"></i>',
    '</a>',
    '<a class="task-rerun mr-3" href="javascript:void(0)" title="Re-run">',
    '<i class="fa fa-redo" style="color: #858796"></i>',
    '</a>',
    '<a class="task-delete" href="javascript:void(0)" title="Delete">',
    '<i class="fa fa-trash" style="color: #858796"></i>',
    '</a>',
  ].join('')
}

window.actionsEvents = {
  "click .task-rerun": function (e, value, row, index) {
    if (!window.confirm("Re-run " + row.tasklet_name + "?")) {
      return;
    }
    axios.put(runs_url + "?id=" + row.id)
      .then(function (response) {
        // console.log(response);
        $("#table").bootstrapTable("refresh", {});
      })
      .catch(function (error) {
        console.log(error);
      });
  }
}
