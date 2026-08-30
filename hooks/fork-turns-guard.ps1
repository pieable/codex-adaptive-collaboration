$ErrorActionPreference = 'Stop'

try {
    $rawInput = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($rawInput)) {
        throw 'Hook input was empty.'
    }

    $event = $rawInput | ConvertFrom-Json -Depth 64
    if ($event.hook_event_name -ne 'PreToolUse') {
        exit 0
    }

    $toolName = [string]$event.tool_name
    $spawnToolNames = @(
        'spawn_agent',
        'Agent',
        'collaboration.spawn_agent',
        'collaborationspawn_agent',
        'multi_agent_v1__spawn_agent'
    )
    if ($toolName -notin $spawnToolNames) {
        exit 0
    }

    $forkTurnsProperty = $event.tool_input.PSObject.Properties['fork_turns']
    $forkTurns = if ($null -eq $forkTurnsProperty -or $null -eq $forkTurnsProperty.Value) {
        '<omitted>'
    }
    else {
        [string]$forkTurnsProperty.Value
    }

    if ($forkTurns -ceq 'none') {
        exit 0
    }

    $reason = 'Blocked subagent creation because fork_turns must be explicitly set to "none". Put the goal, background, action, expected result, and boundaries in a self-contained delegation contract instead of inheriting parent turns.'
    $output = [ordered]@{
        hookSpecificOutput = [ordered]@{
            hookEventName            = 'PreToolUse'
            permissionDecision       = 'deny'
            permissionDecisionReason = $reason
        }
        systemMessage = $reason
    }

    [Console]::Out.WriteLine(($output | ConvertTo-Json -Compress -Depth 8))
    exit 0
}
catch {
    [Console]::Error.WriteLine("fork_turns guard could not validate the spawn_agent call: $($_.Exception.Message)")
    exit 2
}
