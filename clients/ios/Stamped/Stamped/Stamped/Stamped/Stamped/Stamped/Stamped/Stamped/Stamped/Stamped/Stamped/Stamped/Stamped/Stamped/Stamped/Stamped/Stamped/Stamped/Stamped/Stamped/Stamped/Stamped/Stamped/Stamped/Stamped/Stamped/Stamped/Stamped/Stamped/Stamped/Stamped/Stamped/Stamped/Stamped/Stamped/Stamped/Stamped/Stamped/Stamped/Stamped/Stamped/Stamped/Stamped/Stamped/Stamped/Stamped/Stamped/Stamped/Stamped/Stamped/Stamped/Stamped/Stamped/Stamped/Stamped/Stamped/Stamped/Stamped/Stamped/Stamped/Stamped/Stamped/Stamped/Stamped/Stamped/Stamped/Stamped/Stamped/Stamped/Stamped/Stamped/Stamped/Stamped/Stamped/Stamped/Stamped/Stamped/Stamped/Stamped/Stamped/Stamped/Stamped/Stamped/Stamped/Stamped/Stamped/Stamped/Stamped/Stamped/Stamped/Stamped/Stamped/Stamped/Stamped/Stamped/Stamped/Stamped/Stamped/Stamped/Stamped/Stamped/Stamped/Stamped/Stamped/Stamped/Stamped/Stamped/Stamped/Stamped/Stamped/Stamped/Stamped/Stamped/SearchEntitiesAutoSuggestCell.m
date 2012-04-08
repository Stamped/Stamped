//
//  SearchEntitiesAutoSuggestCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 11/2/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "SearchEntitiesAutoSuggestCell.h"

#import <QuartzCore/QuartzCore.h>

#import "UIColor+Stamped.h"

@implementation SearchEntitiesAutoSuggestCell

@synthesize customTextLabel = customTextLabel_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [self initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier];
  if (self) {
    customTextLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(36, 0, 264, 47)];
    customTextLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:16];
    customTextLabel_.textColor = [UIColor stampedBlackColor];
    customTextLabel_.highlightedTextColor = [UIColor whiteColor];
    [self.contentView addSubview:customTextLabel_];
    [customTextLabel_ release];
  }
  return self;
}

- (void)dealloc {
  customTextLabel_ = nil;
  [super dealloc];
}

@end
