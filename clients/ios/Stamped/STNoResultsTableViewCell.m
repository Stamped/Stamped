//
//  STNoResultsTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 2/1/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STNoResultsTableViewCell.h"

#import "UIColor+Stamped.h"

@interface STNoResultsTableViewCell ()
@property (nonatomic, readonly) UILabel* noResultsLabel;
@end

@implementation STNoResultsTableViewCell

@synthesize noResultsLabel = noResultsLabel_;

+ (STNoResultsTableViewCell*)cell {
  return [[[STNoResultsTableViewCell alloc] init] autorelease];
}

- (id)init {
  self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:nil];
  if (self) {
    self.selectionStyle = UITableViewCellSelectionStyleNone;
    noResultsLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    noResultsLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:14];
    noResultsLabel_.textAlignment = UITextAlignmentCenter;
    noResultsLabel_.textColor = [UIColor stampedGrayColor];
    noResultsLabel_.text = @"No Results";
    [noResultsLabel_ sizeToFit];
    [self.contentView addSubview:noResultsLabel_];
    [noResultsLabel_ release];
  }
  return self;
}

- (void)dealloc {
  noResultsLabel_ = nil;
  [super dealloc];
}

- (void)layoutSubviews {
  [super layoutSubviews];
  noResultsLabel_.center = self.contentView.center;
}

@end
