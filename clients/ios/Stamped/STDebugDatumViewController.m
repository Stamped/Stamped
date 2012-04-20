//
//  STDebugDatumViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STDebugDatumViewController.h"
#import <QuartzCore/QuartzCore.h>

@interface STDebugDatumViewController ()

@property (nonatomic, readonly, retain) STDebugDatum* datum;
@property (nonatomic, readonly, retain) UITextView* textView;

@end

@implementation STDebugDatumViewController

@synthesize datum = datum_;
@synthesize textView = textView_;

- (id)initWithDatum:(STDebugDatum*)datum
{
  self = [super init];
  if (self) {
    datum_ = [datum retain];
  }
  return self;
}

- (void)dealloc
{
  [datum_ release];
  [super dealloc];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  CGFloat padding = 5;
  textView_ = [[UITextView alloc] initWithFrame:CGRectMake(padding, 
                                                           padding, 
                                                           self.scrollView.frame.size.width - 2 * padding, 
                                                           self.scrollView.frame.size.height - 2 * padding- 30)];
  textView_.text = [NSString stringWithFormat:@"%@\n%@", self.datum.object, self.datum.created];
  textView_.layer.borderWidth = 2;
  textView_.layer.borderColor = [UIColor colorWithWhite:.7 alpha:1].CGColor;
  [self.scrollView appendChildView:textView_];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
  [textView_ release];
}

@end
