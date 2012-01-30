//
//  STSelectCountryViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 1/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "STTableViewController.h"

@class STSelectCountryViewController;

@protocol STSelectCountryViewControllerDelegate
@required
- (void)viewController:(STSelectCountryViewController*)controller didSelectCountry:(NSString*)country code:(NSString*)countryCode;
@end

@interface STSelectCountryViewController : STTableViewController <UITableViewDelegate, UITableViewDataSource>

- (id)initWithCountryCode:(NSString*)countryCode;

@property (nonatomic, assign) id<STSelectCountryViewControllerDelegate> delegate;

@end
