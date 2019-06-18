using System;
using System.Collections;
using System.Collections.Generic;

public class FirstTreeJson
{
    public bool sendMarkersToEEG;
    public string portalEEGserial;
    public bool showPlayPauseButton;
    public string? leftInputKey;
    public string? centerInputKey;
    public string? rightInputKey;
    public string institution;
    public bool attentionPoint;
    public float attentionDiameter;
    public string attentionColorStart;
    public string attentionColorCorrect;
    public string attentionColorWrong;
    public List<MenuJson> menus;
    public string id;
    public int limitPlays;
    public int choices;
    public int depth;
    public bool readSequ;
    public string sequ;
    public string sequR;
    public int minHitsInSequence;
    public string animationTypeJG;
    public string animationTypeOthers;
    public bool scoreboard;
    public string finalScoreboard;
    public int playsToRelax;
    public bool showHistory;
    public float sppedGKAnim;
    public List<JsonStateInput> states;
}