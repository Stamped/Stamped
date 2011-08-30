//
//  STCategoryDropdownTableView.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/29/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STCategoryDropdownTableView.h"

#import <QuartzCore/QuartzCore.h>

#import "UIColor+Stamped.h"
#import "Util.h"

@interface STCategoryTableViewCell : UITableViewCell

- (id)initWithCategoryRow:(STEditCategoryRow)categoryRow;

@property (nonatomic, readonly) UIImageView* categoryImage;
@property (nonatomic, readonly) UILabel* categoryLabel;
@end

@implementation STCategoryTableViewCell

@synthesize categoryImage = categoryImage_;
@synthesize categoryLabel = categoryLabel_;

- (id)initWithCategoryRow:(STEditCategoryRow)categoryRow {
  self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@""];
  if (self) {
    categoryImage_ = [[UIImageView alloc] initWithFrame:CGRectMake(10, 13, 15, 12)];
    [self.contentView addSubview:categoryImage_];
    [categoryImage_ release];
    categoryLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMaxX(categoryImage_.frame) + 10,
                                                              9,
                                                              CGRectGetWidth(self.bounds) - CGRectGetWidth(categoryImage_.bounds) - 10,
                                                              20)];
    [self.contentView addSubview:categoryLabel_];
    [categoryLabel_ release];

    categoryLabel_.textColor = [UIColor stampedBlackColor];
    categoryLabel_.highlightedTextColor = [UIColor whiteColor];
    categoryLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
    categoryImage_.contentMode = UIViewContentModeScaleAspectFit;

    switch (categoryRow) {
      case STEditCategoryRowFood:
        categoryLabel_.text = @"Restaurants & Bars";
        categoryImage_.image = [UIImage imageNamed:@"cat_icon_food"];
        break;
      case STEditCategoryRowBooks:
        categoryLabel_.text = @"Books";
        categoryImage_.image = [UIImage imageNamed:@"cat_icon_book"];
        break;
      case STEditCategoryRowFilm:
        categoryLabel_.text = @"Film & TV";
        categoryImage_.image = [UIImage imageNamed:@"cat_icon_film"];
        break;
      case STEditCategoryRowMusic:
        categoryLabel_.text = @"Music";
        categoryImage_.image = [UIImage imageNamed:@"cat_icon_music"];
        break;
      case STEditCategoryRowOther:
        categoryLabel_.text = @"Other";
        categoryImage_.image = [UIImage imageNamed:@"cat_icon_other"];
        break;
      default:
        NSLog(@"This should not happen.");
        break;
    }
    categoryImage_.highlightedImage = [Util whiteMaskedImageUsingImage:categoryImage_.image];
  }
  return self;
}

@end

@implementation STCategoryDropdownTableView

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self) {
    self.dataSource = self;
    self.layer.cornerRadius = 5;
    self.layer.borderWidth = 2;
    self.layer.borderColor = [UIColor stampedBlackColor].CGColor;
  }
  return self;
}

#pragma mark - UITableViewDataSource Protocol Methods.

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  return 5;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  STCategoryTableViewCell* cell = [[[STCategoryTableViewCell alloc] initWithCategoryRow:(STEditCategoryRow)indexPath.row] autorelease];

  return (UITableViewCell*)cell;
}

@end
