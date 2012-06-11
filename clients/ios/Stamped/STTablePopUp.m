//
//  STTablePopUp.m
//  Stamped
//
//  Created by Landon Judkins on 4/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STTablePopUp.h"
#import "Util.h"

@interface STTablePopUp ()

- (void)exitTapped:(id)button;

@end

@implementation STTablePopUp

@synthesize header = _header;
@synthesize footer = _footer;
@synthesize table = _table;

- (id)initWithFrame:(CGRect)frame
{
  self = [super initWithFrame:frame];
  if (self) {
    _header = [[UIView alloc] initWithFrame:CGRectMake(0, 0, self.frame.size.width, 0)];
    _footer = [[UIView alloc] initWithFrame:CGRectMake(0, self.frame.size.height, self.frame.size.width, 0)];
    _table = [[UITableView alloc] initWithFrame:CGRectMake(0, 0, self.frame.size.width, self.frame.size.height)];
    [self addSubview:_table];
    [self addSubview:_header];
    [self addSubview:_footer];
    UIImageView* exitIcon = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"popup_wht_closeButton"]] autorelease];
    exitIcon.frame = CGRectOffset(exitIcon.frame, -exitIcon.frame.size.width/2, -exitIcon.frame.size.height/2);
    [self addSubview:exitIcon];
    UIView* exitButton = [Util tapViewWithFrame:CGRectMake(-exitIcon.frame.size.width, 
                                                           -exitIcon.frame.size.height, 
                                                           exitIcon.frame.size.width * 2, 
                                                           exitIcon.frame.size.height * 2) 
                                         target:self
                                       selector:@selector(exitTapped:) 
                                     andMessage:nil];
    [self addSubview:exitButton];
    _table.scrollsToTop = YES;
    _table.delegate = self;
    _table.dataSource = self;
  }
  return self;
}

- (id)init {
  return [self initWithFrame:[Util centeredAndBounded:CGSizeMake(280, 400) inFrame:[UIApplication sharedApplication].keyWindow.frame]];
}

- (void)dealloc
{
  [_footer release];
  [_header release];
  [_table release];
  [super dealloc];
}

- (void)exitTapped:(id)button {
  [Util setFullScreenPopUp:nil dismissible:NO withBackground:nil];
}

- (void)childView:(UIView*)view shouldChangeHeightBy:(CGFloat)delta overDuration:(CGFloat)seconds {
  if (view == self.header) {
    [UIView animateWithDuration:seconds animations:^{
      [Util reframeView:view withDeltas:CGRectMake(0, 0, 0, delta)];
      [Util reframeView:self.table withDeltas:CGRectMake(0, delta, 0, -delta)];
    }];
  }
  else if (view == self.footer) {
    [UIView animateWithDuration:seconds animations:^{
      [Util reframeView:view withDeltas:CGRectMake(0, -delta, 0, delta)];
      [Util reframeView:self.table withDeltas:CGRectMake(0, 0, 0, -delta)];
    }];
  }
  else if (view == self.table) {
    [UIView animateWithDuration:seconds animations:^{
      [Util reframeView:self.table withDeltas:CGRectMake(0, 0, 0, delta)];
      [Util reframeView:self.footer withDeltas:CGRectMake(0, delta, 0, 0)];
      [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, delta)];
    }];
  }
  else {
    //NSLog(@"Unknown child view (%@) changedHeight in %@", view, self);
    NSAssert(NO, @"unknown child");
  }
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  return 0;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  return 1;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  return nil;
}


- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
}



@end
