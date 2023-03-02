const RunLogsApp = {
    delimiters: ['[[', ']]'],
    props: ['run_websocket_url', 'query_websocket_url', 'logs_ts_now'],
    data() {
        return {
            state: 'idle',
            websocket: undefined,
            retry_interval: undefined,
            connection_retry_timeout: 5000,
            logs_pull_end: 0,
            logs_tail_ts: 0,
            logs_query_limit: 1000,
            logs_tail_limit: 1000,
            logs: []
        }

    },
    mounted() {
      this.state = 'initializing'
      this.logs_pull_end = BigInt(this.logs_ts_now)
      this.logs_tail_ts = BigInt(this.logs_ts_now) + BigInt(1)
      this.init()
    },
    computed: {
        reversedLogs: function () {
            return this.logs.slice().reverse()
        },
        websocket_url: function () {
            return this.run_websocket_url + '&start=' + this.logs_tail_ts.toString() + '&limit=' + this.logs_tail_limit.toString()
        },
    },
    template: `
        <div class="card card-12 mb-5">
            <div class="card-header">
                <div class="row">
                    <div class="col-2"><h3>Logs ([[ state ]])</h3></div>
                </div>
            </div>
            <div class="card-body card-table">
              <div id="logs-body" class="card-body overflow-auto pt-0 pl-3">
                  <ul class="list-group">
                      <li v-for="line in reversedLogs" class="list-group-item">
                          <div style="word-break: break-all; white-space: pre-wrap;">[[ line ]]</div>
                      </li>
                  </ul>
              </div>
            </div>
        </div>
    `,
    methods: {
        init() {
            this.state = 'pulling'
            this.init_websocket()
            axios.get(
                this.query_websocket_url + '&start=0' + '&end=' + this.logs_pull_end.toString() + '&limit=' + this.logs_query_limit.toString(),
                {
                  withCredentials: true,
                }
            )
              .then(this.on_pull_reply)
              .catch(this.on_pull_error)
        },
        on_pull_reply(response) {
            console.log("Response:")
            console.log(response)
        },
        on_pull_error(error) {
            console.log("Error:")
            console.log(error)
            // this.init_websocket()
        },
        init_websocket() {
            this.state = 'connecting'
            this.websocket = new WebSocket(this.websocket_url)
            this.websocket.onmessage = this.on_websocket_message
            this.websocket.onopen = this.on_websocket_open
            this.websocket.onclose = this.on_websocket_close
            this.websocket.onerror = this.on_websocket_error
        },
        on_websocket_open(message) {
            this.state = 'connected'
        },
        on_websocket_message(message) {
            if (message.type !== 'message') {
                console.warn('Unknown message from socket', message)
                return
            }

            const data = JSON.parse(message.data)
            let current_items = []

            data.streams.forEach(stream_item => {
                stream_item.values.forEach(message_item => {
                    current_items.push({
                      "ts": BigInt(message_item[0]),
                      "message": message_item[1],
                    })
                })
            })

            current_items.sort((first, second) => {
                if (first["ts"] > second["ts"]) {
                    return 1;
                } else if (first["ts"] < second["ts"]) {
                    return -1;
                } else {
                    return 0;
                }
            });

            current_items.forEach(current_item => {
                this.logs.push(current_item["message"])
                this.logs_tail_ts = current_item["ts"] + BigInt(1)
            })
        },
        on_websocket_close(message) {
            this.state = 'disconnected'
            this.retry_interval = setInterval(() => {
                clearInterval(this.retry_interval)
                this.init_websocket()
            }, this.connection_retry_timeout)
        },
        on_websocket_error(message) {
            this.state = 'error'
            this.websocket.close()
        }
    }
}

vueApp.component('runlogsapp', RunLogsApp)
