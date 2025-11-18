{{/*
Common labels
*/}}
{{- define "apiLabels" -}}
{{- toYaml .Values.labels.api }}
{{- end }}

{{- define "minioLabels" -}}
{{- toYaml .Values.labels.minio }}
{{- end }}
{}