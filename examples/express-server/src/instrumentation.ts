/*instrumentation.js*/
import { NodeSDK } from "@opentelemetry/sdk-node";
import { resourceFromAttributes } from "@opentelemetry/resources";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";

import {
  ATTR_SERVICE_NAME,
  ATTR_SERVICE_VERSION,
} from "@opentelemetry/semantic-conventions";

import { PrometheusExporter } from "@opentelemetry/exporter-prometheus";
import { ZipkinExporter } from "@opentelemetry/exporter-zipkin";

const prometheusExporter = new PrometheusExporter(
  {
    port: 9090,
    endpoint: "/metrics",
  },
  () => {
    console.log("Prometheus started on port 9090");
  },
);

const sdk = new NodeSDK({
  resource: resourceFromAttributes({
    [ATTR_SERVICE_NAME]: "ecomerce-api",
    [ATTR_SERVICE_VERSION]: "0.1.0",
  }),

  instrumentations: [
    getNodeAutoInstrumentations({
      "@opentelemetry/instrumentation-fs": {
        enabled: false,
      },
    }),
  ],

  traceExporter: new ZipkinExporter(),
  metricReader: prometheusExporter,
});

sdk.start();
