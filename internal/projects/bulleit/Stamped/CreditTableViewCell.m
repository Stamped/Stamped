//
//  CreditTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "CreditTableViewCell.h"

#import <QuartzCore/QuartzCore.h>

#import "Entity.h"
#import "Stamp.h"
#import "User.h"
#import "Util.h"
#import "UIColor+Stamped.h"

@implementation CreditTableViewCell

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault
              reuseIdentifier:reuseIdentifier];
  if (self) {
    UIImage* disclosureImage = [UIImage imageNamed:@"disclosure_arrow"];
    UIImageView* disclosureArrowImageView = [[UIImageView alloc] initWithFrame:CGRectMake(290, 28, 8, 11)];
    disclosureArrowImageView.contentMode = UIViewContentModeCenter;
    disclosureArrowImageView.image = disclosureImage;
    disclosureArrowImageView.highlightedImage = [Util whiteMaskedImageUsingImage:disclosureImage];
    [self.contentView addSubview:disclosureArrowImageView];
    [disclosureArrowImageView release];
  }
          
  return self;
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated{
  [super setSelected:selected animated:animated];

  // Configure the view for the selected state
}

@end
