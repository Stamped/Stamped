//
//  PairedLabel.m
//  Stamped
//
//  Created by Jake Zien on 9/9/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "PairedLabel.h"

@implementation PairedLabel

@synthesize nameLabel   = nameLabel_;
@synthesize valueLabel  = valueLabel_;
@synthesize nameWidth   = nameWidth_;
@synthesize numberWidth = numberWidth_;

static const CGFloat kTextLabelGutterWidth = 20.f;
static const CGFloat kNumberLabelGutterWidth = 8.f;

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
      nameWidth_ =  0.f;
      numberWidth_= 0.f;
    }
    return self;
}

- (void)didReceiveMemoryWarning
{
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  // Release any retained subviews of the main view.
  // e.g. self.myOutlet = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  // Return YES for supported orientations
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (void)setNameWidth:(CGFloat)newWidth
{
  nameWidth_ = newWidth;

  CGRect frame = nameLabel_.frame;
  frame.size.width = nameWidth_;
  nameLabel_.frame = frame;
  
  frame = valueLabel_.frame;
  frame.size.width = CGRectGetWidth(self.view.frame) - CGRectGetWidth(nameLabel_.frame) - kTextLabelGutterWidth * 2;
  frame.origin.x = CGRectGetMaxX(nameLabel_.frame) + kTextLabelGutterWidth;
  
  frame.size = [valueLabel_.text sizeWithFont:valueLabel_.font 
                            constrainedToSize:CGSizeMake(frame.size.width, HUGE_VAL)
                                lineBreakMode:UILineBreakModeWordWrap];
  valueLabel_.frame = frame;

  NSUInteger lineCt = [self lineCountOfLabel:valueLabel_];
  if (lineCt > 1)
    self.view.frame = CGRectMake(self.view.frame.origin.x, self.view.frame.origin.y, 
                                 self.view.frame.size.width, lineCt * valueLabel_.font.lineHeight + 10);
  [self.view setNeedsDisplay];
}


- (void)setNumberWidth:(CGFloat)newWidth
{
  numberWidth_ = newWidth;
  
  CGRect frame = nameLabel_.frame;
  frame.size.width = numberWidth_;
  nameLabel_.frame = frame;
  nameLabel_.contentMode = UIViewContentModeBottomLeft;
  
  frame = valueLabel_.frame;
  frame.size.width = CGRectGetWidth(self.view.frame) - CGRectGetWidth(nameLabel_.frame) - kNumberLabelGutterWidth * 4;
  frame.origin.x = CGRectGetMaxX(nameLabel_.frame) + kNumberLabelGutterWidth;
  
  frame.size = [valueLabel_.text sizeWithFont:valueLabel_.font 
                            constrainedToSize:CGSizeMake(frame.size.width, HUGE_VAL)
                                lineBreakMode:UILineBreakModeWordWrap];
  valueLabel_.frame = frame;

  NSUInteger lineCt = [self lineCountOfLabel:valueLabel_];
  if (lineCt > 1) 
    self.view.frame = CGRectMake(self.view.frame.origin.x, self.view.frame.origin.y, 
                                 self.view.frame.size.width, lineCt * valueLabel_.font.lineHeight);
  [self.view setNeedsDisplay];
}

- (NSUInteger)lineCountOfLabel:(UILabel *)label {  
  CGRect frame = label.frame;
  frame.size.width = label.frame.size.width;
  frame.size = [label sizeThatFits:frame.size];
  CGFloat lineHeight = label.font.lineHeight;
  NSUInteger linesInLabel = floor(frame.size.height/lineHeight);
  return linesInLabel;
}




@end
