//
//  BookDetailViewController.h
//  Stamped
//
//  Created by Jake Zien on 9/11/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "EntityDetailViewController.h"

@interface FilmDetailViewController : EntityDetailViewController

@property (nonatomic, retain) IBOutlet UIImageView* imageView;
@property (nonatomic, retain) IBOutlet UIImageView* affiliateLogoView;
@property (nonatomic, retain) IBOutlet UIImageView* ratingView;

@end
