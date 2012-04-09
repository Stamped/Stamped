//
//  STInboxViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STInboxViewController.h"
#import "STStampsView.h"

@interface STInboxViewController () <UIPickerViewDelegate, UIPickerViewDataSource>

@end

@implementation STInboxViewController

- (id)init
{
  self = [super init];
  if (self) {
    //pass
  }
  return self;
}

- (void)viewDidLoad
{
  [super viewDidLoad];
 // UIPickerView* picker = [[[UIPickerView alloc] initWithFrame:CGRectMake(0, 0, 320, 20)] autorelease];
  //picker.delegate = self;
  //picker.dataSource = self;
  //[self.scrollView appendChildView:picker];
  STStampsView* view = [[[STStampsView alloc] initWithFrame:CGRectMake(0, 0, 320, 363)] autorelease];
  //view.backgroundColor = [UIColor redColor];
  STGenericCollectionSlice* slice = [[STGenericCollectionSlice alloc] init];
  slice.offset = [NSNumber numberWithInt:0];
  slice.limit = [NSNumber numberWithInt:NSIntegerMax];
  slice.sort = @"created";
  view.slice = slice;
  self.scrollView.scrollsToTop = NO;
  [self.scrollView appendChildView:view];
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
}
- (NSInteger)numberOfComponentsInPickerView:(UIPickerView *)pickerView {
  return 1;
}

- (NSInteger)pickerView:(UIPickerView *)pickerView numberOfRowsInComponent:(NSInteger)component {
  return 10;
}

- (void)pickerView:(UIPickerView *)pickerView didSelectRow:(NSInteger)row inComponent:(NSInteger)component {
  NSLog(@"selected:%d,%d",row,component);
}

- (NSString *)pickerView:(UIPickerView *)pickerView titleForRow:(NSInteger)row forComponent:(NSInteger)component {
  return [NSString stringWithFormat:@"Row:%d",row];
}

- (CGFloat)pickerView:(UIPickerView *)pickerView rowHeightForComponent:(NSInteger)component {
  return 50;
}

- (CGFloat)pickerView:(UIPickerView *)pickerView widthForComponent:(NSInteger)component {
  return 100;
}

@end
