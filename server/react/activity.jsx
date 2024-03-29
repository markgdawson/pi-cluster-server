import React from 'react';
import ReactDOM from 'react-dom';
import {
  Avatar,
  ClusterSchematic
} from './clusterschematic.jsx';

import {
  SimulationList
} from './simulationlist.jsx';

import {
  colourJob
} from './receivesimulations.jsx';

import css from '../assets/styles/activity.sass';

//const data_url = "http://10.0.0.254:3524/cluster/activity";
const data_url = "/cluster/activity";

class Layout extends React.Component {
  constructor(props) {
    super(props);

    const cores = 16;
    // map of labels provided by server to layout of the cluster
    // in the schematic in the client
    const clusterLayout = [
      ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4"],
      ["10.0.0.5", "10.0.0.6", "10.0.0.7", "10.0.0.8"],
      ["10.0.0.9", "10.0.0.10", "10.0.0.11", "10.0.0.12"],
      ["10.0.0.13", "10.0.0.14", "10.0.0.253", "10.0.0.254"]
    ];

    this.state = {
      clusterLayout: clusterLayout,
      nodeInfo: clusterLayout.map((row) =>
        row.map((col) => {
          return {
            job: {},
            cpuHistory: [],
            cpuColourHistory: []
          };
        })
      ),
      cpuHistoryMax: 50,
      serverUpdateInterval: 0.5, // update time in seconds
      dataUrl: data_url,
      pending: [],
      running: [],
      last_fetch: '- - -',
      last_fetch_error: true,
    };

  }

  componentDidMount() {
    window.addEventListener('load', this.scheduleNextUpdate.bind(this));
  }

  buildJobMap(jobs) {
    // Build and returns a map of node_id -> job object from a joblist
    var job_map = {};

    jobs.forEach((job) => {
      job['nodes'].forEach((node_id) => {
        job_map[node_id] = job;
      });
    });

    return job_map;
  }

  // fetch best simulations from server and update in component state
  fetchActivity() {
    fetch(this.state.dataUrl, {
        mode: 'cors'
      })
      .then(res => res.json())
      .then(
        (result) => {

          this.setState({
            last_fetch: this.formatUnixEpoch(result.time),
            last_fetch_error: false,
          });

          const running = result.running.map((job) => colourJob(job));
          const pending = result.pending.map((job) => colourJob(job));
          const job_map = this.buildJobMap(running);

          // map the cpu activity to each core
          const mappedInfo = this.state.clusterLayout.map((rows,
            row_idx) => {
            return rows.map((node_id, col_idx) => {
              var info = this.state.nodeInfo[row_idx][col_idx];
              info.node_id = node_id;

              const job = colourJob(job_map[node_id]);

              const temp = result.temp_percent[node_id];

              info.temp = temp;

              info.job = job;
              info.cpuHistory.push(result.cpu_usage[node_id]);
              info.cpuColourHistory.push(job.colour);

              // limit length to this.state.cpuHistoryMax
              const start = info.cpuHistory.length - this.state
                .cpuHistoryMax;
              const end = info.cpuHistory.length;

              if (start >= 0) {
                info.cpuHistory = info.cpuHistory.slice(start, end);
                info.cpuColourHistory = info.cpuColourHistory.slice(
                  start,
                  end);
              }

              return info;
            });
          });

          this.setState({
            nodeInfo: mappedInfo,
            pending: pending,
            running: running,

          });

          this.scheduleNextUpdate();
        },
        (error) => {
          this.setState({
            last_fetch_error: true
          });
          this.scheduleNextUpdate();;
        }
      );
  }

  formatUnixEpoch(epoch) {
    const date = new Date(epoch * 1000);
    return date.getHours() + ":" + date.getMinutes() + ":" + date
      .getSeconds();
  }

  // start periodic poll of the cluster
  scheduleNextUpdate() {
    setTimeout(this.fetchActivity.bind(this), this.state
      .serverUpdateInterval * 1000);
  }

  render() {
    return (
      <div id="layout">
	    <RecentFetch last_fetch={this.state.last_fetch} last_fetch_error={this.state.last_fetch_error} />
          <div className="pane lhs">
              <ClusterSchematic info={this.state.nodeInfo} />
          </div>
          <SimulationList simulations={this.state.running} title="Running" percentageKey='progress'/>
          <SimulationList simulations={this.state.pending} title="Waiting" percentageKey='progress'/>
      </div>
    );
  }
}

function RecentFetch(props) {
  const className = "last-fetch-time " +
    (props.last_fetch_error ? "error" : "");

  return (
    <div className={className}>{props.last_fetch}</div>
  );
}

ReactDOM.render(
  <Layout />,
  document.getElementById('root-activity')
);
