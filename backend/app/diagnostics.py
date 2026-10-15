"""Evidence-based, read-only Kueue and workload diagnostics for synthetic telemetry.

Kueue admission is based on ClusterQueue quota, resource flavors, cohorts,
borrowing, and workload admission checks; this module never mutates clusters.
"""
import re


def _number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def diagnose(incident):
    """Return transparent findings with evidence and safe next steps.

    Missing signals remain unknown; no live Kubernetes state is inferred.
    """
    metrics = incident.get('metrics') or {}
    logs = [str(line) for line in incident.get('logs', [])]
    text = '\n'.join(logs)
    findings = []
    recommendations = []
    evidence = []
    pending = _number(metrics.get('pending'))
    running = _number(metrics.get('running'))
    failed = _number(metrics.get('failed'))
    passed = _number(metrics.get('passed'))
    if pending is not None and pending > 0:
        findings.append({'category': 'scheduling', 'severity': 'warning',
                         'finding': f'{int(pending)} workloads reported pending; pending alone does not establish a quota issue.',
                         'evidence': ['metrics.pending'], 'confidence': 'high'})
        evidence.append(f'metrics.pending={int(pending)}')
    quota = re.search(r'cohort\s+quota\s+cpu\s+(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)\s+used', text, re.I)
    quota_full = False
    if quota:
        used, limit = map(float, quota.groups())
        quota_full = limit > 0 and used >= limit
        if quota_full:
            findings.append({'category': 'admission', 'severity': 'high',
                             'finding': f'Observed CPU quota usage {used:g}/{limit:g}; the reported quota is fully used.',
                             'evidence': [quota.group(0)], 'confidence': 'high'})
            evidence.append(quota.group(0))
    insufficient = any('admission check insufficient cpu quota' in x.lower() for x in logs)
    if insufficient:
        findings.append({'category': 'admission', 'severity': 'high',
                         'finding': 'A workload admission check explicitly reported insufficient CPU quota.',
                         'evidence': [x for x in logs if 'admission check insufficient cpu quota' in x.lower()],
                         'confidence': 'high'})
        recommendations.extend([
            'Inspect LocalQueue and ClusterQueue admission conditions, resource flavor selection, and pending Workload status.',
            'Check cohort borrowing limits, nominal quotas, and available resources before proposing a quota adjustment.',
            'Request platform-owner approval for any quota or workload configuration change.'
        ])
    elif pending and pending > 0:
        recommendations.append('Inspect pending Workload status and admission conditions before attributing backlog to quota.')
    oom_lines = [x for x in logs if re.search(r'\bOOMKilled\b', x, re.I)]
    if oom_lines:
        findings.append({'category': 'execution', 'severity': 'high',
                         'finding': 'A worker was reported OOMKilled. This is an execution/memory failure, not proof of a scheduling admission problem.',
                         'evidence': oom_lines, 'confidence': 'high'})
        evidence.extend(oom_lines)
        recommendations.extend([
            'Inspect terminated pod status, memory request/limit, peak usage, and the worker logs.',
            'Consider memory right-sizing or workload partitioning after reproducing the failure; require approval before changes.'
        ])
    if failed is not None and failed > 0 and not oom_lines:
        findings.append({'category': 'execution', 'severity': 'warning',
                         'finding': f'{int(failed)} failed workers reported; termination causes are not provided.',
                         'evidence': ['metrics.failed'], 'confidence': 'medium'})
        recommendations.append('Inspect failed pod termination reasons and recent logs.')
    if not findings:
        findings.append({'category': 'general', 'severity': 'info',
                         'finding': 'Insufficient structured scheduling or worker-failure signals for a specific diagnosis.',
                         'evidence': [], 'confidence': 'low'})
    if quota_full and insufficient:
        cause = 'Evidence supports CPU quota exhaustion blocking at least one Kueue admission; verify scope and current ClusterQueue state.'
        confidence = 'high'
    elif insufficient:
        cause = 'Kueue admission reported insufficient CPU quota; exact capacity and cohort state need verification.'
        confidence = 'medium'
    elif oom_lines:
        cause = 'Worker memory termination observed; cause of memory pressure is not established.'
        confidence = 'medium'
    else:
        cause = 'Insufficient evidence to confirm a specific root cause.'
        confidence = 'low'
    return {'probable_cause': cause, 'confidence': confidence,
            'findings': findings, 'evidence': evidence[:10],
            'recommendations': list(dict.fromkeys(recommendations)),
            'telemetry': {'pending': pending, 'running': running, 'failed': failed, 'passed': passed},
            'data_source': 'synthetic-incident-snapshot', 'read_only': True}
