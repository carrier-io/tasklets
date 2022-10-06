$("#btn-refresh").click(function() {
  $("#table").bootstrapTable("refresh", {});
});

function actionsFormatter(value, row, index) {
  return [
    '<a class="task-view mr-3" href="' + run_logs_url + '?id=' + row.id + '" title="View">',
    '<i class="fa fa-list" style="color: #858796"></i>',
    '</a>',
    '<a class="task-delete" href="javascript:void(0)" title="Delete">',
    '<i class="fa fa-trash" style="color: #858796"></i>',
    '</a>',
  ].join('')
}

window.actionsEvents = {
}
