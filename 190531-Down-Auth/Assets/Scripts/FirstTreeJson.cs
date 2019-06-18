using System;
using System.Collections;
using System.Collections.Generic;

public class FirstTreeJson
{
    public string id { get; set; }
    public int? limitPlays { get; set; }
    public int choices { get; set; }
    public int? depth { get; set; }
    public bool readSequ { get; set; }
    public string sequ { get; set; }
    public string sequR { get; set; }
    public List<JsonStateInput> states { get; set; }
    public int? minHitsInSequence { get; set; }
    public string animationTypeJG { get; set; }
    public string animationTypeOthers { get; set; }
    public bool scoreboard { get; set; }
    public string groupCode { get; set; }
    public string finalScoreboard { get; set; }
    public int playsToRelax { get; set; }
    public bool showHistory { get; set; }
    public string sendMarkersToEEG { get; set; }
    public string portalEEGserial { get; set; }
    public bool showPlayPauseButton { get; set; }
    public string pausePlayInputKey { get; set; }
    public string leftInputKey { get; set; }
    public string centerInputKey { get; set; }
    public string rightInputKey { get; set; }
    public string institution { get; set; }
    public bool attentionPoint { get; set; }
    public double attentionDiameter { get; set; }
    public string attentionColorStart { get; set; }
    public string attentionColorCorrect { get; set; }
    public string attentionColorWrong { get; set; }
    public double speedGKAnim { get; set; }
    public List<MenuJson> menus { get; set; }
}