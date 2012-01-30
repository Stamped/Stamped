//
//  STSelectCountryTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 1/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STSelectCountryTableViewCell : UITableViewCell

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, readonly) UILabel* countryLabel;
@property (nonatomic, assign) BOOL checked;

@end
