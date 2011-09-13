//
//  BookDetailViewController.h
//  Stamped
//
//  Created by Jake Zien on 9/11/11.
//  Copyright 2011 RISD. All rights reserved.
//

#import "EntityDetailViewController.h"

@interface FilmDetailViewController : EntityDetailViewController

@property (nonatomic, retain) IBOutlet UIImageView* imageView;
@property (nonatomic, retain) IBOutlet UIImageView* affiliateLogoView;
@property (nonatomic, retain) IBOutlet UIImageView* ratingView;

@end
