//
//  PairedLabel.m
//  Stamped
//
//  Created by Jake Zien on 9/9/11.
//  Copyright 2011 RISD. All rights reserved.
//

#import "PairedLabel.h"

@implementation PairedLabel

@synthesize nameLabel   = nameLabel_;
@synthesize valueLabel  = valueLabel_;
@synthesize nameWidth   = nameWidth_;
@synthesize numberWidth = numberWidth_;

static const CGFloat kTextLabelGutterWidth = 30.f;
static const CGFloat kNumberLabelGutterWidth = 4.f;

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

- (void)viewDidLoad
{
    [super viewDidLoad];
    // Do any additional setup after loading the view from its nib.
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
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
  frame.size.width += CGRectGetWidth(self.view.frame) - CGRectGetWidth(nameLabel_.frame) - kTextLabelGutterWidth;
  frame.origin.x = CGRectGetMaxX(nameLabel_.frame) + kTextLabelGutterWidth;
  valueLabel_.frame = frame;
}


- (void)setNumberWidth:(CGFloat)newWidth
{
  numberWidth_ = newWidth;
  
  CGRect frame = nameLabel_.frame;
  frame.size.width = numberWidth_;
  nameLabel_.frame = frame;
  
  frame = valueLabel_.frame;
  frame.size.width += CGRectGetWidth(self.view.frame) - CGRectGetWidth(nameLabel_.frame) - kNumberLabelGutterWidth;
  frame.origin.x = CGRectGetMaxX(nameLabel_.frame) + kNumberLabelGutterWidth;
  valueLabel_.frame = frame;
}

@end
